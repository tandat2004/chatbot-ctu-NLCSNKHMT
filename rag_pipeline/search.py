"""Tìm kiếm ngữ nghĩa (kết hợp BM25) trên cơ sở tri thức CTU.

Dùng như thư viện:
    from search import KnowledgeBase
    kb = KnowledgeBase()
    hits = kb.search("Học phí học kỳ 1 đóng khi nào?", k=5, topics=["hoc_phi"])
    prompt_context = kb.format_context(hits)   # đưa vào prompt của LLM

Dùng dòng lệnh:
    python search.py "ký túc xá đăng ký thế nào" -k 5
    python search.py "hoc phi" --topic hoc_phi
    python search.py            # chế độ hỏi-đáp tương tác
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from textutil import parse_date, tokenize


@dataclass
class Hit:
    id: str
    text: str
    metadata: dict
    score: float                      # điểm sau khi trộn (RRF) — chỉ dùng để xếp hạng
    similarity: Optional[float] = None  # cosine của nhánh ngữ nghĩa (None nếu chỉ khớp BM25)
    sources: list[str] = field(default_factory=list)  # 'semantic' / 'bm25'

    @property
    def needs_review(self) -> bool:
        d = parse_date(self.metadata.get("kiem_tra_lai_vao"))
        return bool(d and d < date.today())

    @property
    def expired(self) -> bool:
        d = parse_date(self.metadata.get("hieu_luc_den"))
        return bool(d and d < date.today())

    @property
    def low_confidence(self) -> bool:
        return self.similarity is None or self.similarity < config.LOW_CONFIDENCE_SIM


class KnowledgeBase:
    def __init__(self, vector_dir: Path = config.VECTOR_DIR, model: Optional[str] = None):
        import chromadb

        self.client = chromadb.PersistentClient(path=str(Path(vector_dir).resolve()))
        try:
            self.col = self.client.get_collection(config.COLLECTION_NAME)
        except Exception as e:  # noqa: BLE001
            raise SystemExit(f"Chưa có cơ sở tri thức tại {vector_dir}. Hãy chạy build_index.py trước.") from e
        # Dùng đúng model đã dùng khi index (tránh lệch không gian vector)
        self.model_name = model or (self.col.metadata or {}).get("embedding_model") or config.EMBEDDING_MODEL
        self._embedder = None
        self._bm25 = None

    # ---- nội bộ ------------------------------------------------------------------
    @property
    def embedder(self):
        if self._embedder is None:
            from embedder import get_embedder
            self._embedder = get_embedder(self.model_name)
        return self._embedder

    def _where(self, topics, chunk_type):
        conds = []
        if topics:
            conds.append({"topic": topics[0]} if len(topics) == 1 else {"topic": {"$in": list(topics)}})
        if chunk_type:
            conds.append({"chunk_type": chunk_type})
        if not conds:
            return None
        return conds[0] if len(conds) == 1 else {"$and": conds}

    def _ensure_bm25(self):
        if self._bm25 is None:
            from rank_bm25 import BM25Okapi
            data = self.col.get(include=["documents", "metadatas"])
            self._b_ids, self._b_docs, self._b_metas = data["ids"], data["documents"], data["metadatas"]
            self._bm25 = BM25Okapi([tokenize(d) for d in self._b_docs])

    def _semantic(self, query, n, where):
        n = min(n, self.col.count())
        res = self.col.query(query_embeddings=[self.embedder.embed_query(query)], n_results=n,
                             where=where, include=["documents", "metadatas", "distances"])
        return [(i, d, m, 1.0 - dist) for i, d, m, dist in
                zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])]

    def _keyword(self, query, n, topics, chunk_type):
        self._ensure_bm25()
        scores = self._bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out = []
        for i in order:
            if scores[i] <= 0:
                break
            m = self._b_metas[i]
            if topics and m.get("topic") not in topics:
                continue
            if chunk_type and m.get("chunk_type") != chunk_type:
                continue
            out.append((self._b_ids[i], self._b_docs[i], m, scores[i]))
            if len(out) >= n:
                break
        return out

    # ---- API chính ---------------------------------------------------------------
    def search(self, query: str, k: int = config.DEFAULT_TOP_K, topics: Optional[list[str]] = None,
               chunk_type: Optional[str] = None, hybrid: bool = True,
               faq_boost: float = config.FAQ_BOOST) -> list[Hit]:
        """Trả về top-k Hit. `topics`: lọc theo chủ đề (vd ['hoc_phi']). `chunk_type`: 'faq' | 'doc'."""
        query = unicodedata.normalize("NFC", query)
        n = max(k * 4, 20)
        sem = self._semantic(query, n, self._where(topics, chunk_type))
        hits: dict[str, Hit] = {}
        for rank, (i, d, m, sim) in enumerate(sem, 1):
            hits[i] = Hit(i, d, m, 1.0 / (config.RRF_K + rank), similarity=sim, sources=["semantic"])
        if hybrid:
            for rank, (i, d, m, _) in enumerate(self._keyword(query, n, topics, chunk_type), 1):
                if i in hits:
                    hits[i].score += 1.0 / (config.RRF_K + rank)
                    hits[i].sources.append("bm25")
                else:
                    hits[i] = Hit(i, d, m, 1.0 / (config.RRF_K + rank), sources=["bm25"])
        for h in hits.values():
            if h.metadata.get("chunk_type") == "faq":
                h.score *= faq_boost
        return sorted(hits.values(), key=lambda h: h.score, reverse=True)[:k]

    @staticmethod
    def format_context(hits: list[Hit]) -> str:
        """Định dạng kết quả thành khối ngữ cảnh kèm nguồn + cảnh báo, để đưa vào prompt LLM."""
        blocks = []
        for n, h in enumerate(hits, 1):
            m = h.metadata
            info = [m.get("doc_title", "")]
            if m.get("so_hieu"):
                info.append(f"số hiệu {m['so_hieu']}")
            if m.get("hieu_luc_tu"):
                info.append(f"hiệu lực từ {m['hieu_luc_tu']}")
            if m.get("hoc_ky_ap_dung"):
                info.append(f"áp dụng {m['hoc_ky_ap_dung']}")
            warn = []
            if h.expired:
                warn.append("VĂN BẢN ĐÃ HẾT HIỆU LỰC")
            if h.needs_review:
                warn.append(f"đã quá hạn kiểm tra lại ({m.get('kiem_tra_lai_vao')}), thông tin có thể đã cũ")
            head = f"[{n}] Nguồn: {' | '.join(x for x in info if x)}"
            if warn:
                head += "\n    ⚠ " + "; ".join(warn)
            blocks.append(f"{head}\n{h.text}")
        return "\n\n---\n\n".join(blocks)


def _print_hits(hits: list[Hit]) -> None:
    if not hits:
        print("  (không có kết quả)")
    for n, h in enumerate(hits, 1):
        m = h.metadata
        sim = f"{h.similarity:.3f}" if h.similarity is not None else "  -  "
        flags = []
        if h.expired:
            flags.append("HẾT HIỆU LỰC")
        if h.needs_review:
            flags.append("CẦN KIỂM TRA LẠI")
        if h.low_confidence:
            flags.append("độ tin cậy thấp")
        print(f"\n#{n}  sim={sim}  [{'+'.join(h.sources)}]  {m.get('chunk_type')}/{m.get('topic')}"
              + (f"  ⚠ {', '.join(flags)}" if flags else ""))
        print(f"    Nguồn: {m.get('source_file')}" + (f" — {m['so_hieu']}" if m.get("so_hieu") else ""))
        preview = h.text.replace("\n", " ")
        print("    " + (preview[:300] + "…" if len(preview) > 300 else preview))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", help="Câu hỏi; bỏ trống để vào chế độ tương tác")
    ap.add_argument("-k", type=int, default=config.DEFAULT_TOP_K)
    ap.add_argument("--topic", action="append", help="Lọc theo chủ đề (có thể lặp lại)")
    ap.add_argument("--type", choices=["faq", "doc"], dest="chunk_type")
    ap.add_argument("--no-hybrid", action="store_true", help="Chỉ dùng tìm kiếm ngữ nghĩa")
    ap.add_argument("--vector-dir", type=Path, default=config.VECTOR_DIR)
    args = ap.parse_args()

    kb = KnowledgeBase(args.vector_dir)
    run = lambda q: _print_hits(kb.search(q, args.k, args.topic, args.chunk_type, not args.no_hybrid))  # noqa: E731
    if args.query:
        run(args.query)
        return
    print("Nhập câu hỏi (Enter trống để thoát).")
    while True:
        q = input("\n❓ ").strip()
        if not q:
            break
        run(q)


if __name__ == "__main__":
    main()
