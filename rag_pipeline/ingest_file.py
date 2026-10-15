"""
ingest_file.py — Tự động nạp 1 tài liệu mới (PDF / DOCX) vào hệ thống RAG:
1. Tự động đọc và bóc tách bố cục (dùng Docling qua process_docs_gpt.py)
2. Cắt chunk và cập nhật nối tiếp vào data_pipeline/data/2_processed/chunks.jsonl
3. Vector hóa (Embedding) và nạp trực tiếp vào ChromaDB (collection ctu_knowledge_base)
4. Kiểm tra truy vấn thử nghiệm ngay lập tức.

Cách dùng (chạy từ thư mục gốc hoặc rag_pipeline/):
    python ingest_file.py "data_pipeline/data/1_raw/ten_file.pdf"
    python ingest_file.py "ten_file.pdf"
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi UnicodeEncodeError
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "rag_pipeline" else BASE_DIR

DATA_PIPELINE_DIR = PROJECT_ROOT / "data_pipeline"
CHUNKS_FILE = DATA_PIPELINE_DIR / "data" / "2_processed" / "chunks.jsonl"
PROCESS_DOCS_SCRIPT = DATA_PIPELINE_DIR / "process_docs_gpt.py"
DB_PATH = str(BASE_DIR / "db" / "chroma_db")
COLLECTION_NAME = "ctu_knowledge_base"
EMBED_MODEL = "BAAI/bge-m3"


def find_target_file(user_path_str: str) -> Path:
    p = Path(user_path_str)
    if p.is_file():
        return p.resolve()
    
    # Thử tìm trong data/1_raw
    raw_candidate = DATA_PIPELINE_DIR / "data" / "1_raw" / user_path_str
    if raw_candidate.is_file():
        return raw_candidate.resolve()

    # Thử tìm tương đối theo working directory
    cur_candidate = Path.cwd() / user_path_str
    if cur_candidate.is_file():
        return cur_candidate.resolve()

    return None


def run_document_chunking(target_file: Path) -> bool:
    print("\n" + "=" * 60)
    print(f"BƯỚC 1: Xử lý và băm chunk tài liệu bằng Docling...")
    print(f"File nguồn: {target_file.name}")
    print("=" * 60)

    cmd = [
        sys.executable,
        str(PROCESS_DOCS_SCRIPT),
        "--input", str(target_file),
        "--output", str(DATA_PIPELINE_DIR / "data" / "2_processed"),
    ]

    res = subprocess.run(cmd, cwd=str(DATA_PIPELINE_DIR), text=True)
    if res.returncode != 0:
        print("[LỖI] Xử lý tài liệu thất bại ở process_docs_gpt.py!")
        return False
    return True


def embed_chunks_to_chroma(target_filename: str):
    import chromadb
    from chromadb.utils import embedding_functions

    print("\n" + "=" * 60)
    print("BƯỚC 2: Trích xuất chunks mới và nhúng vào ChromaDB...")
    print("=" * 60)

    if not CHUNKS_FILE.exists():
        print(f"[LỖI] Không tìm thấy file {CHUNKS_FILE}")
        return False

    # Lấy các chunks thuộc về file vừa xử lý
    items = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            src = c.get("source_file", "")
            if src == target_filename or Path(src).name == target_filename:
                text = c.get("text_with_context") or c.get("text")
                if not text:
                    continue
                items.append({
                    "id": f"doc-{c['chunk_id']}",
                    "text": text,
                    "metadata": {
                        "chunk_type": "doc",
                        "source_file": src,
                        "title": c.get("title", ""),
                        "section": c.get("section", ""),
                        "page": str(c.get("page", "")),
                    }
                })

    if not items:
        print(f"[CẢNH BÁO] Không tìm thấy chunks nào cho file '{target_filename}' trong {CHUNKS_FILE}")
        return False

    print(f"-> Tìm thấy {len(items)} chunks cần nhúng cho file '{target_filename}'.")

    print(f"-> Đang kết nối ChromaDB tại '{DB_PATH}'...")
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)
    old_count = collection.count()

    print(f"-> Đang tạo vector embedding bằng mô hình {EMBED_MODEL}...")
    batch_size = 20
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        collection.upsert(
            documents=[b["text"] for b in batch],
            metadatas=[b["metadata"] for b in batch],
            ids=[b["id"] for b in batch],
        )
        print(f"   Đã lưu {min(i + batch_size, len(items))}/{len(items)} chunks")

    new_count = collection.count()
    print(f"\n[HOÀN TẤT] Nạp thành công {len(items)} chunks!")
    print(f"Tổng số mục trong ChromaDB hiện tại: {new_count} (trước đó: {old_count})")

    # Kiểm tra truy vấn thử nghiệm
    print("\n" + "=" * 60)
    print("BƯỚC 3: Kiểm tra thử nghiệm truy vấn tài liệu vừa nạp...")
    print("=" * 60)
    sample_text = items[0]["text"][:60]
    test_query = items[0]["metadata"]["title"] or sample_text
    print(f"Thử tìm kiếm với từ khóa tiêu đề: '{test_query}'")
    results = collection.query(query_texts=[test_query], n_results=min(2, len(items)))
    for idx, (doc, meta, dist) in enumerate(zip(results["documents"][0], results["metadatas"][0], results["distances"][0])):
        print(f"  Top {idx+1} [Khoảng cách: {dist:.4f}]:")
        print(f"  Nguồn: {meta.get('source_file')} | Mục: {meta.get('section')}")
        print(f"  Trích đoạn: {doc[:150]}...\n")

    return True


def main():
    ap = argparse.ArgumentParser(description="Tự động bóc tách và nhúng 1 file tài liệu mới vào ChromaDB.")
    ap.add_argument("file", help="Đường dẫn đến file .pdf hoặc .docx cần nạp")
    args = ap.parse_args()

    target_file = find_target_file(args.file)
    if not target_file:
        print(f"[LỖI] Không tìm thấy file: '{args.file}'")
        print(f"Hãy kiểm tra lại đường dẫn hoặc đặt file vào thư mục '{DATA_PIPELINE_DIR / 'data' / '1_raw'}'")
        sys.exit(1)

    # Bước 1: Parse & chunk
    success = run_document_chunking(target_file)
    if not success:
        sys.exit(1)

    # Bước 2: Embed & upsert vào ChromaDB
    success = embed_chunks_to_chroma(target_file.name)
    if not success:
        sys.exit(1)

    print("=" * 60)
    print("🎉 THÀNH CÔNG!")
    print("Tài liệu mới đã sẵn sàng trong cơ sở dữ liệu của Chatbot.")
    print("Lưu ý: Nếu đang chạy 'api.py' hoặc 'generate.py', hãy khởi động lại để nhận dữ liệu mới.")
    print("=" * 60)


if __name__ == "__main__":
    main()
