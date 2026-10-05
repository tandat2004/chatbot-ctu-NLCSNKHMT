"""
build_vector_db.py — Gộp chunk tài liệu (2_processed/chunks.jsonl) và FAQ
(3_faq/*.csv) rồi nhúng vào ChromaDB. Dùng BAAI/bge-m3 (không dùng MiniLM).

Cách dùng (chạy từ thư mục rag_pipeline\\):
    python build_vector_db.py --preview      # chỉ xem trước, KHÔNG nhúng, không tốn thời gian
    python build_vector_db.py                # build thật

Script tự đoán tên cột câu hỏi / câu trả lời / nguồn trong CSV dựa trên các
từ khóa phổ biến. Nếu đoán sai, dùng --q-col --a-col --src-col để chỉ tay.
"""
import argparse
import csv
import json
import os
import re
from pathlib import Path

IMG_MD_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def clean_text(text: str) -> str:
    """Cắt bỏ cú pháp ảnh markdown ![...](...) lẫn trong câu trả lời,
    vì đây là rác hiển thị ảnh từ nền tảng khác, không phải nội dung thật."""
    text = IMG_MD_PATTERN.sub("", text)
    # Dọn bớt dòng trống thừa do vừa cắt ảnh
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

import chromadb
from chromadb.utils import embedding_functions

EMBED_MODEL = "BAAI/bge-m3"
DB_PATH = "./db/chroma_db"
COLLECTION_NAME = "ctu_knowledge_base"

CHUNKS_FILE = Path("data/2_processed/chunks.jsonl")
FAQ_DIR = Path("data/3_faq")

Q_HINTS = ["cau_hoi", "câu hỏi", "cauhoi", "question"]
A_HINTS = ["tra_loi", "trả lời", "traloi", "answer"]
SRC_HINTS = ["nguon", "nguồn", "source"]


def guess_col(fieldnames, hints):
    low = {f: f.lower() for f in fieldnames}
    for f, l in low.items():
        if any(h in l for h in hints):
            return f
    return None


def load_doc_chunks():
    items = []
    if not CHUNKS_FILE.exists():
        print(f"[CẢNH BÁO] Không thấy {CHUNKS_FILE}, bỏ qua phần chunk tài liệu.")
        return items
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            text = c.get("text_with_context") or c.get("text")
            if not text:
                continue
            items.append({
                "id": f"doc-{c['chunk_id']}",
                "text": text,
                "metadata": {
                    "chunk_type": "doc",
                    "source_file": c.get("source_file", ""),
                    "title": c.get("title", ""),
                    "section": c.get("section", ""),
                    "page": str(c.get("page", "")),
                },
            })
    print(f"Đọc được {len(items)} chunk tài liệu từ {CHUNKS_FILE}")
    return items


def load_faq_csv(q_col=None, a_col=None, src_col=None):
    items = []
    csv_files = sorted(FAQ_DIR.glob("*.csv"))
    if not csv_files:
        print(f"[CẢNH BÁO] Không thấy file .csv nào trong {FAQ_DIR}")
        return items

    for path in csv_files:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            qc = q_col or guess_col(fieldnames, Q_HINTS)
            ac = a_col or guess_col(fieldnames, A_HINTS)
            sc = src_col or guess_col(fieldnames, SRC_HINTS)
            print(f"\nFile: {path.name}")
            print(f"  Cột tìm thấy: {fieldnames}")
            print(f"  -> dùng làm câu hỏi: {qc!r} | câu trả lời: {ac!r} | nguồn: {sc!r}")
            if not qc or not ac:
                print("  [LỖI] Không đoán được cột câu hỏi/câu trả lời — bỏ qua file này."
                      " Dùng --q-col --a-col để chỉ tay.")
                continue

            for i, row in enumerate(reader):
                q = clean_text((row.get(qc) or "").strip())
                a = clean_text((row.get(ac) or "").strip())
                if not q or not a:
                    continue
                src = (row.get(sc) or "").strip() if sc else ""
                text = f"Câu hỏi: {q}\nTrả lời: {a}"
                items.append({
                    "id": f"faq-{path.stem}-{i}",
                    "text": text,
                    "metadata": {
                        "chunk_type": "faq",
                        "source_file": src or path.name,
                        "title": q[:80],
                        "section": "",
                        "page": "",
                    },
                })
    print(f"\nĐọc được tổng cộng {len(items)} FAQ từ {len(csv_files)} file CSV")
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="Chỉ xem trước, không nhúng")
    ap.add_argument("--q-col", default=None)
    ap.add_argument("--a-col", default=None)
    ap.add_argument("--src-col", default=None)
    ap.add_argument("--batch-size", type=int, default=100)
    args = ap.parse_args()

    doc_items = load_doc_chunks()
    faq_items = load_faq_csv(args.q_col, args.a_col, args.src_col)
    all_items = doc_items + faq_items

    print("\n" + "=" * 60)
    print(f"TỔNG: {len(doc_items)} chunk tài liệu + {len(faq_items)} FAQ = {len(all_items)} mục")

    if faq_items:
        print("\n--- Xem trước 3 FAQ đầu tiên ---")
        for it in faq_items[:3]:
            print(f"  [{it['id']}] {it['text'][:150]}...")

    if args.preview:
        print("\nĐây là chế độ --preview, CHƯA nhúng gì cả.")
        print("Nếu cột đã đúng, chạy lại không có --preview để build thật.")
        return

    if not all_items:
        print("Không có dữ liệu để nhúng, dừng lại.")
        return

    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)

    print(f"\nĐang tải mô hình embedding {EMBED_MODEL} (lần đầu sẽ mất thời gian tải ~2GB)...")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    # Xóa collection cũ nếu có, để không bị lẫn dữ liệu của lần build trước
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Đã xóa collection cũ '{COLLECTION_NAME}' để build lại sạch.")
    except Exception:  # noqa: BLE001
        pass
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    print(f"\nBắt đầu nhúng {len(all_items)} mục...")
    for i in range(0, len(all_items), args.batch_size):
        batch = all_items[i : i + args.batch_size]
        collection.add(
            documents=[b["text"] for b in batch],
            metadatas=[b["metadata"] for b in batch],
            ids=[b["id"] for b in batch],
        )
        print(f"  Đã lưu {min(i + args.batch_size, len(all_items))}/{len(all_items)}")

    print(f"\n[HOÀN TẤT] Đã build {len(all_items)} mục vào '{DB_PATH}' (collection: {COLLECTION_NAME})")

    print("\n--- TEST TÌM KIẾM ---")
    test_query = "Học phí học lại là bao nhiêu?"
    print(f"Câu hỏi: '{test_query}'\n")
    results = collection.query(query_texts=[test_query], n_results=3)
    for idx, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"Kết quả {idx + 1} [{meta.get('chunk_type', '?')}]:")
        print(f"  Nguồn: {meta.get('source_file', '')} (Mục: {meta.get('section', '')})")
        print(f"  Trích đoạn: {doc[:300]}...\n")


if __name__ == "__main__":
    main()
