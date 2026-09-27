"""Xây dựng cơ sở tri thức: đọc processed/ + faq/ -> chia đoạn -> embedding -> ChromaDB.

Cách dùng:
    python build_index.py --dry-run      # chỉ chia đoạn, xuất chunks_preview.jsonl để kiểm tra
    python build_index.py                # chạy đầy đủ (xóa & dựng lại collection)
    python build_index.py --data-dir D:/Data_CTU_restructured --model intfloat/multilingual-e5-base

Quy ước phân loại file:
  * File có tên bắt đầu bằng "faq" (không phân biệt hoa/thường), nằm trong faq/ HOẶC processed/,
    được coi là FAQ: mỗi cặp Hỏi-Đáp = 1 chunk.
  * File khác trong processed/ là tài liệu thường: chia đoạn theo heading.
  * File trong faq/ mà tên KHÔNG bắt đầu bằng "faq" (vd bao_cao_khao_sat.md) bị BỎ QUA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from chunker import chunk_markdown, word_count
from faq_parser import faq_header_info, parse_faq
from metadata import META_FIELDS, RawMetaIndex, sanitize, split_front_matter

TEXT_EXTS = {".md", ".txt"}
SHORT_CHUNK_WORDS = 20


def _read(path: Path) -> str:
    # NFC: file chuyển từ PDF thường ở dạng NFD (dấu tách rời) -> embedding/BM25 khớp kém với câu hỏi gõ NFC
    return unicodedata.normalize("NFC", path.read_text(encoding="utf-8-sig", errors="replace"))


def _cid(*parts: str) -> str:
    return hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()[:20]


def _doc_title(meta: dict, body: str, stem: str) -> str:
    if meta.get("tieu_de"):
        return str(meta["tieu_de"]).strip()
    m = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    return m.group(1).strip() if m else stem.replace("_", " ")


def _is_faq_name(p: Path) -> bool:
    return p.stem.lower().startswith("faq")


def _faq_topic(stem: str) -> str:
    t = re.sub(r"^faq[_\-\s]*", "", stem, flags=re.I)
    return config.FAQ_TOPIC_ALIASES.get(t.lower(), t)


def collect_chunks(data_dir: Path) -> tuple[list[dict], dict]:
    processed, faq_dir, raw = data_dir / "processed", data_dir / "faq", data_dir / "raw"
    if not processed.exists():
        raise SystemExit(f"Không thấy thư mục {processed}. Dùng --data-dir để chỉ đúng vị trí.")

    meta_index = RawMetaIndex(raw)
    map_file = data_dir / "processed_meta_map.json"  # (tùy chọn) {"processed/x/a.md": "raw_name.pdf"}
    overrides = json.loads(map_file.read_text(encoding="utf-8-sig")) if map_file.exists() else {}
    chunks: list[dict] = []
    report = {"warnings": list(meta_index.warnings), "skipped": [],
              "per_topic": defaultdict(lambda: defaultdict(int))}

    # ---- Phân loại file ----------------------------------------------------------
    all_processed = [p for p in sorted(processed.rglob("*"))
                     if p.suffix.lower() in TEXT_EXTS and not p.name.lower().startswith(("readme", "_"))]
    doc_paths = [p for p in all_processed if not _is_faq_name(p)]
    faq_items = [(p, p.parent.name) for p in all_processed if _is_faq_name(p)]  # (file, chủ đề)
    if faq_dir.exists():
        for p in sorted(faq_dir.glob("*.md")):
            if p.stem.lower() in ("faq_template", "readme"):
                continue
            if _is_faq_name(p):
                faq_items.append((p, _faq_topic(p.stem)))
            else:
                report["skipped"].append(p.relative_to(data_dir).as_posix())

    n_per_folder: dict[str, int] = defaultdict(int)
    for p in doc_paths:
        n_per_folder[p.parent.name] += 1
    known_topics = set(n_per_folder) | {p.parent.name for p in all_processed}

    # ---- 1. Tài liệu thường ------------------------------------------------------
    for path in doc_paths:
        folder = path.parent.name if path.parent != processed else "khac"
        rel = path.relative_to(data_dir).as_posix()

        front, body = split_front_matter(_read(path))
        raw_meta, status = meta_index.find(folder, path.stem, n_per_folder[path.parent.name],
                                           body_head=body[:3000], override=overrides.get(rel, ""))
        meta = dict(front)
        meta.update({k: v for k, v in raw_meta.items() if v not in (None, "")})
        if status not in ("matched", "override"):
            note = {"so_hieu": "ghép theo số hiệu văn bản trong nội dung — nên kiểm tra lại",
                    "topic-single": "dùng metadata của file raw duy nhất trong thư mục — nên kiểm tra lại",
                    "none": "KHÔNG tìm thấy .meta.json (metadata sẽ trống). "
                            "Thêm vào processed_meta_map.json hoặc đặt tên file trùng với file raw"}[status]
            report["warnings"].append(f"[meta:{status}] {rel} — {note}")

        title = _doc_title(meta, body, path.stem)
        # `topic` = tên thư mục (khớp tên chủ đề FAQ, dùng để lọc); topic khai trong meta để riêng
        base = {"topic": folder, "meta_topic": meta.get("topic", ""), "source_file": rel,
                "doc_title": title, "chunk_type": "doc", "meta_match": status}
        base.update({k: meta.get(k, "") for k in META_FIELDS if k != "tieu_de"})

        so_hieu = str(meta.get("so_hieu") or "").strip()
        label = f"{title} ({so_hieu})" if so_hieu and so_hieu not in title else title
        pieces = chunk_markdown(body, title, config.CHUNK_MAX_WORDS, config.CHUNK_MIN_WORDS,
                                config.CHUNK_OVERLAP_WORDS, doc_label=label)
        for i, p in enumerate(pieces):
            md = dict(base, section=p["section"], chunk_index=i, word_count=word_count(p["text"]))
            chunks.append({"id": _cid(rel, str(i)), "text": p["text"], "metadata": sanitize(md)})
        report["per_topic"][folder]["docs"] += 1
        report["per_topic"][folder]["doc_chunks"] += len(pieces)

    # ---- 2. FAQ: mỗi cặp Hỏi-Đáp là 1 chunk ------------------------------------
    for path, topic in faq_items:
        rel = path.relative_to(data_dir).as_posix()
        front, body = split_front_matter(_read(path))
        pairs = parse_faq(body)
        expected = len(re.findall(r"^#{1,6}\s*FAQ[-_]", body, re.M))  # số mục "### FAQ-xxx-001"
        if topic not in known_topics:
            report["warnings"].append(
                f"[faq-topic] {rel} — chủ đề '{topic}' không trùng thư mục nào trong processed/ "
                f"(lọc theo chủ đề sẽ không khớp). Khai báo FAQ_TOPIC_ALIASES trong config.py")
        if not pairs:
            report["warnings"].append(f"[faq] {rel} — đọc được 0 cặp hỏi-đáp (kiểm tra định dạng)")
        elif expected and expected != len(pairs):
            report["warnings"].append(
                f"[faq] {rel} — có {expected} mục FAQ-xxx nhưng chỉ đọc được {len(pairs)} cặp (kiểm tra định dạng)")

        info = faq_header_info(body)
        title = front.get("tieu_de") or f"FAQ {topic}"
        for i, (q, a, fid) in enumerate(pairs):
            text = f"Câu hỏi: {q}\nTrả lời: {a}"
            md = {"topic": topic, "source_file": rel, "doc_title": title, "chunk_type": "faq",
                  "faq_id": fid, "question": q, "section": "", "chunk_index": i,
                  "word_count": word_count(text), "nguon_tham_khao": info["nguon_tham_khao"],
                  "hoc_ky_ap_dung": meta_index.topic_hoc_ky(topic),
                  "kiem_tra_lai_vao": meta_index.earliest_review_date(topic)}
            chunks.append({"id": _cid(rel, "faq", str(i)), "text": text, "metadata": sanitize(md)})
        report["per_topic"][topic]["faq"] += len(pairs)
        report["per_topic"][topic]["faq_files"] += 1
    return chunks, report


def print_report(chunks: list[dict], report: dict) -> None:
    print("\n=== THỐNG KÊ CHUNK ===")
    print(f"{'Chủ đề':<20}{'Tài liệu':>9}{'Chunk-doc':>11}{'File FAQ':>10}{'Cặp FAQ':>9}")
    for topic, s in sorted(report["per_topic"].items()):
        print(f"{topic:<20}{s['docs']:>9}{s['doc_chunks']:>11}{s['faq_files']:>10}{s['faq']:>9}")
    wcs = [c["metadata"]["word_count"] for c in chunks]
    if wcs:
        print(f"\nTổng {len(chunks)} chunk | từ/chunk: min {min(wcs)}, TB {sum(wcs)//len(wcs)}, max {max(wcs)}")
    n_faq = sum(1 for c in chunks if c["metadata"]["chunk_type"] == "faq")
    print(f"Tổng số cặp FAQ: {n_faq}")

    short = [c for c in chunks if c["metadata"]["chunk_type"] == "doc"
             and c["metadata"]["word_count"] < SHORT_CHUNK_WORDS]
    if short:
        print(f"\nChunk tài liệu rất ngắn (<{SHORT_CHUNK_WORDS} từ): {len(short)} — ví dụ:")
        for c in short[:5]:
            print(f"   - {c['metadata']['source_file']}: {c['text'][:90]!r}")
    if report["skipped"]:
        print("\n=== FILE BỊ BỎ QUA (nằm trong faq/ nhưng tên không bắt đầu bằng 'faq') ===")
        for s in report["skipped"]:
            print(" -", s)
    if report["warnings"]:
        print("\n=== CẢNH BÁO ===")
        for w in report["warnings"]:
            print(" -", w)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=Path, default=config.DATA_DIR)
    ap.add_argument("--vector-dir", type=Path, default=config.VECTOR_DIR)
    ap.add_argument("--model", default=config.EMBEDDING_MODEL)
    ap.add_argument("--dry-run", action="store_true", help="Chỉ chia đoạn + xuất chunks_preview.jsonl")
    args = ap.parse_args()

    t0 = time.time()
    chunks, report = collect_chunks(args.data_dir.resolve())
    print_report(chunks, report)
    if not chunks:
        raise SystemExit("Không có chunk nào — kiểm tra lại đường dẫn dữ liệu.")

    if args.dry_run:
        out = Path("chunks_preview.jsonl")
        with out.open("w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps({"id": c["id"], **c["metadata"], "text": c["text"]}, ensure_ascii=False) + "\n")
        print(f"\nĐã ghi {out.resolve()} — mở ra xem chunk có hợp lý không trước khi embed.")
        return

    import chromadb
    from embedder import get_embedder

    embedder = get_embedder(args.model)
    print(f"\nĐang tạo embedding cho {len(chunks)} chunk...")
    vectors = embedder.embed_passages([c["text"] for c in chunks])

    client = chromadb.PersistentClient(path=str(args.vector_dir.resolve()))
    try:
        client.delete_collection(config.COLLECTION_NAME)  # dựng lại từ đầu cho nhất quán
    except Exception:  # noqa: BLE001
        pass
    col = client.create_collection(
        config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": args.model},
    )
    B = 100
    for i in range(0, len(chunks), B):
        part = chunks[i:i + B]
        col.upsert(ids=[c["id"] for c in part], documents=[c["text"] for c in part],
                   metadatas=[c["metadata"] for c in part], embeddings=vectors[i:i + B])
    print(f"\n✔ Đã lưu {col.count()} chunk vào {args.vector_dir.resolve()} "
          f"(model: {args.model}) trong {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
