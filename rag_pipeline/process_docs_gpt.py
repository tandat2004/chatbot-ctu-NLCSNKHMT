#!/usr/bin/env python3
"""
process_docs_gpt.py (Cập nhật dùng Docling)
Pipeline xử lý tài liệu cho RAG + AI enrichment có cấu trúc.

Thay đổi chính:
- Dùng Docling để phân tích layout, đọc bảng biểu, header/footer cực chuẩn.
- Hỗ trợ xuất trực tiếp ra Markdown tự động cho cả PDF và DOCX.

Cài đặt:
    pip install openai docling

Chạy cơ bản (Chỉ băm và trích xuất Metadata theo luật heuristc):
    python process_docs_gpt.py --input raw/downloaded_files --output processed

Chạy nâng cao (Dùng AI trích xuất và sinh câu hỏi):
    python process_docs_gpt.py --input raw/downloaded_files --output processed --gpt-metadata --gpt-questions 3
"""

import argparse
import csv
import hashlib
import json
import os
import re
import time
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

# Khởi tạo Docling Converter
try:
    from docling.document_converter import DocumentConverter
    print("[Hệ thống] Đang khởi tạo mô hình Docling... (Có thể mất vài giây cho lần chạy đầu tiên)")
    doc_converter = DocumentConverter()
except ImportError:
    raise RuntimeError("Chưa cài đặt Docling. Hãy chạy: pip install docling")


# ---------------------------------------------------------------------------
# Basic utilities

def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def strip_accents(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def sha1(s, n=10):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:n]


def compact_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Document Readers (Sử dụng Docling)

def read_document_docling(path):
    """
    Sử dụng Docling để đọc và phân tích cấu trúc tài liệu (PDF, DOCX).
    Tự động đọc bảng (table), tiêu đề, layout và chuyển thành Markdown.
    """
    try:
        result = doc_converter.convert(str(path))
        doc = result.document
        
        # Lấy tổng số trang
        n_pages = len(doc.pages) if hasattr(doc, "pages") and doc.pages else None
        
        # Export nội dung sang định dạng Markdown chuẩn
        md_text = doc.export_to_markdown()
        
        paras = []
        # Tách Markdown thành các đoạn văn bản (paragraphs) dựa trên 2 dấu xuống dòng
        for block in md_text.split("\n\n"):
            block_str = block.strip()
            if block_str:
                paras.append({"text": block_str, "page": None})
                
        needs_ocr = False  # Docling tự xử lý OCR nếu cần
        return paras, n_pages, needs_ocr, md_text
        
    except Exception as e:
        print(f"   [Docling Lỗi] Không thể đọc file {path.name}: {e}")
        return [], 0, False, ""


# ---------------------------------------------------------------------------
# Cleaning

JUNK = re.compile(
    r"^(Signature (Valid|Not Verified)|Ký bởi:|Ký ngày:|Digitally signed|Reason:|Location:)",
    re.I,
)
PAGE_NO = re.compile(
    r"^(-?\s*\d{1,3}\s*-?|Trang\s+\d+(\s*/\s*\d+)?|\d+\s*/\s*\d+)$",
    re.I,
)

def clean_paras(paras):
    out = []
    for p in paras:
        t = nfc(p["text"]).replace("\u00a0", " ").replace("\u200b", "")
        t = re.sub(r"[ \t]+", " ", t).strip()
        if not t or JUNK.match(t) or PAGE_NO.match(t):
            continue
        out.append({"text": t, "page": p["page"]})
    return out


# ---------------------------------------------------------------------------
# Heuristic metadata

TITLE_RE = re.compile(
    r"\b(QUYẾT ĐỊNH|THÔNG BÁO|KẾ HOẠCH|QUY ĐỊNH|QUY CHẾ|QUY TRÌNH|HƯỚNG DẪN|CÔNG VĂN|"
    r"ĐƠN(?!\s+VỊ)|PHỤ LỤC|BIÊN BẢN|CHƯƠNG TRÌNH)\b"
)

TYPE_SLUG = {
    "QUYẾT ĐỊNH": "quyet_dinh", "THÔNG BÁO": "thong_bao", "KẾ HOẠCH": "ke_hoach",
    "QUY ĐỊNH": "quy_dinh", "QUY CHẾ": "quy_che", "QUY TRÌNH": "quy_trinh",
    "HƯỚNG DẪN": "huong_dan", "CÔNG VĂN": "cong_van", "ĐƠN": "don",
    "PHỤ LỤC": "phu_luc", "BIÊN BẢN": "bien_ban", "CHƯƠNG TRÌNH": "chuong_trinh",
}

FILENAME_TYPES = [
    ("quyet dinh", "quyet_dinh"), ("thong bao", "thong_bao"),
    ("ke hoach", "ke_hoach"), ("quy dinh", "quy_dinh"),
    ("quy che", "quy_che"), ("quy trinh", "quy_trinh"),
    ("huong dan", "huong_dan"), ("cong van", "cong_van"),
    ("don ", "don"), ("phu luc", "phu_luc"),
]

def detect_type(fname, head):
    m = TITLE_RE.search(head[:1500])
    if m:
        return TYPE_SLUG[m.group(1)]

    f = strip_accents(fname.lower()).replace("_", " ")
    for key, slug in FILENAME_TYPES:
        if key in f:
            return slug
    return "khac"

def detect_date(fname, head):
    m = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(20\d{2})", head[:3000], re.I)
    if m:
        d, mo, y = map(int, m.groups())
    else:
        m = re.search(r"(\d{1,2})[-.](\d{1,2})[-.](20\d{2})", fname)
        if m:
            d, mo, y = map(int, m.groups())
        else:
            m = re.search(r"(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})", fname)
            if not m: return None
            y, mo, d = map(int, m.groups())
    try:
        return datetime(y, mo, d).strftime("%Y-%m-%d")
    except ValueError:
        return None

def detect_cohorts(fname, head):
    s = fname + " " + head[:1500]
    found = set(re.findall(r"\bK\s?(\d{2})\b", s))
    found |= set(re.findall(r"[Kk]hóa\s+(\d{2})\b", s))
    return sorted("K" + x for x in found)

def detect_title(doc_type, fname, paras, head):
    m = re.search(r"(?:V/v|Về việc|về việc)\s*:?\s*([^\n]{10,250})", head[:3000])
    label = {v: k.capitalize() for k, v in TYPE_SLUG.items()}.get(doc_type, "")
    if m:
        return (label + " về việc " + m.group(1).strip()).strip()

    for p in paras[:15]:
        text = p["text"]
        if (text.isupper() and len(text) >= 12 and "CỘNG HÒA" not in text and "ĐỘC LẬP" not in text and "TRƯỜNG" not in text):
            return text.title()

    return nfc(Path(fname).stem).replace("_", " ")

def extract_metadata(path, paras):
    head = "\n".join(p["text"] for p in paras[:40])
    doc_type = detect_type(path.name, head)
    so_hieu = re.search(r"Số\s*:?\s*([0-9A-Za-zĐđ\-./]+/[0-9A-Za-zĐđ\-./]+)", head[:3000])
    date = detect_date(path.name, head)
    nam_hoc = re.search(r"năm học\s+(20\d{2})\s*[-–]\s*(20\d{2})", head + " " + path.name, re.I)
    fl = strip_accents(path.stem.lower()).replace("_", " ")
    is_form = (
        doc_type in ("don", "phu_luc")
        or bool(re.search(r"\b(don xin|mau|phieu)\b", fl))
        or bool(re.search(r"ĐƠN(?!\s+VỊ)", head[:400]))
    )

    return {
        "title": detect_title(doc_type, path.name, paras, head),
        "doc_type": doc_type,
        "so_hieu": so_hieu.group(1) if so_hieu else None,
        "ngay_ban_hanh": date,
        "nam": int(date[:4]) if date else (int(re.search(r"20\d{2}", path.name).group()) if re.search(r"20\d{2}", path.name) else None),
        "nam_hoc": f"{nam_hoc.group(1)}-{nam_hoc.group(2)}" if nam_hoc else None,
        "khoa": detect_cohorts(path.name, head),
        "is_form": is_form,
    }


# ---------------------------------------------------------------------------
# Chunking

HARD = re.compile(r"^(#+|CHƯƠNG|Chương|ĐIỀU|Điều)\s+[\dIVXLC]+")
SOFT = re.compile(r"^(\*|-|[IVX]+[\.\)]|\d+(\.\d+)*[\.\)])\s+\S")

def split_long(text, max_chars):
    sents = re.split(r"(?<=[.;!?])\s+", text)
    out, cur = [], ""

    for s in sents:
        if cur and len(cur) + len(s) + 1 > max_chars:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur: out.append(cur)

    res = []
    for o in out:
        while len(o) > max_chars * 1.5:
            cut = o.rfind(" ", 0, max_chars)
            cut = cut if cut > 0 else max_chars
            res.append(o[:cut])
            o = o[cut:].strip()
        res.append(o)
    return res

def chunk_doc(paras, max_chars, min_chars, overlap):
    chunks, cur = [], []
    st = {"len": 0, "new": 0, "page": None, "section": "", "arts": []}
    chapter, article = "", ""

    def section():
        return " > ".join(x for x in (chapter, article) if x)

    def flush(carry):
        if not cur or st["new"] == 0:
            return

        text = "\n".join(cur).strip()
        chunks.append({
            "text": text,
            "section": st["section"],
            "page": st["page"],
            "dieu": ", ".join(st["arts"]),
        })

        tail = text[-overlap:] if (carry and overlap) else ""
        if tail and " " in tail:
            tail = tail[tail.find(" ") + 1:]

        cur.clear()
        st.update(len=0, new=0, arts=[])
        if tail:
            cur.append(tail)
            st["len"] = len(tail)

    for p in paras:
        t, page = p["text"], p["page"]
        
        # Bỏ qua các đường kẻ Markdown sinh ra từ Docling (ví dụ: |---|---|)
        if re.match(r"^\|(?:-+|:-+|-+:|:-+:)(?:\|(?:-+|:-+|-+:|:-+:))+\|$", t):
            cur.append(t)
            st["len"] += len(t) + 1
            st["new"] += len(t)
            continue
            
        is_hard = bool(HARD.match(t))
        is_soft = bool(SOFT.match(t)) and len(t) < 150

        if is_hard:
            if "chương" in t.lower() or t.startswith("# "):
                chapter, article = t[:120], ""
                flush(carry=False)
            else:
                article = t[:120]
                if st["new"] >= min_chars: flush(carry=False)
        elif is_soft and st["new"] >= min_chars:
            flush(carry=False)

        pieces = split_long(t, max_chars) if len(t) > max_chars else [t]
        for piece_index, piece in enumerate(pieces):
            if cur and st["len"] + len(piece) + 1 > max_chars and st["new"] >= min_chars:
                flush(carry=True)
            if st["new"] == 0:
                st["section"] = section()
                st["page"] = page if page else st["page"]

            if is_hard and piece_index == 0 and not "chương" in t.lower():
                m = re.match(r"^\S+\s+\d+|^\S+\s+[IVXLC]+", t)
                if m: st["arts"].append(m.group(0))

            cur.append(piece)
            st["len"] += len(piece) + 1
            st["new"] += len(piece)

    flush(carry=False)
    return chunks


# ---------------------------------------------------------------------------
# OpenAI Structured Outputs (Tương thích GPT/Gemini/Groq)

GPT_METADATA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "doc_type": {
            "type": "string",
            "enum": ["quyet_dinh", "thong_bao", "ke_hoach", "quy_dinh", "quy_che", "quy_trinh", "huong_dan", "cong_van", "don", "phu_luc", "bien_ban", "chuong_trinh", "khac"],
        },
        "so_hieu": {"type": ["string", "null"]},
        "ngay_ban_hanh": {"type": ["string", "null"]},
        "nam_hoc": {"type": ["string", "null"]},
        "khoa": {"type": "array", "items": {"type": "string"}},
        "issuing_agency": {"type": ["string", "null"]},
        "scope": {"type": ["string", "null"]},
        "effective_date": {"type": ["string", "null"]},
        "expiry_date": {"type": ["string", "null"]},
        "supersedes": {"type": ["string", "null"]},
        "is_form": {"type": "boolean"},
        "topics": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "evidence": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "title", "doc_type", "so_hieu", "ngay_ban_hanh", "nam_hoc", "khoa",
        "issuing_agency", "scope", "effective_date", "expiry_date",
        "supersedes", "is_form", "topics", "confidence", "evidence"
    ],
}

GPT_QUESTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "question": {"type": "string"},
                    "intent": {"type": "string", "enum": ["definition", "condition", "procedure", "deadline", "fee", "exception", "document", "authority", "source", "comparison", "scenario"]},
                    "answer_type": {"type": "string", "enum": ["fact", "procedure", "list", "condition", "deadline", "calculation", "scenario"]},
                },
                "required": ["question", "intent", "answer_type"],
            },
        }
    },
    "required": ["questions"],
}

def get_openai_client():
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Thiếu thư viện openai. Chạy: pip install openai") from exc

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("[Cảnh báo] Chưa có OPENAI_API_KEY. Sẽ chỉ dùng luật Heuristic.")
        return None
        
    # Bạn có thể config base_url ở đây để trỏ qua Groq hoặc API tương thích OpenAI khác
    base_url = os.getenv("OPENAI_BASE_URL", None)
    return OpenAI(api_key=key, base_url=base_url)

def gpt_json(client, model, system_prompt, user_prompt, schema_name, schema):
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": schema,
                "strict": True,
            }
        },
    )
    return json.loads(response.output_text.strip())

def gpt_enrich_metadata(client, model, filename, heuristic_meta, head_text):
    system = """Bạn là bộ phận kiểm định metadata cho kho tri thức đại học.
Chỉ trích xuất thông tin được hỗ trợ trực tiếp bởi văn bản đầu vào. Không suy đoán."""
    user = f"""Tên file: {filename}\n\nMetadata heuristic:\n{compact_json(heuristic_meta)}\n\nPhần đầu tài liệu:\n{head_text[:12000]}"""
    return gpt_json(client, model, system, user, "ctu_document_metadata", GPT_METADATA_SCHEMA)

def gpt_generate_questions(client, model, title, section, text, n):
    system = "Bạn tạo câu hỏi kiểm thử cho chatbot tư vấn sinh viên dựa trên văn bản."
    user = f"Tiêu đề: {title}\nMục: {section}\nĐoạn nguồn:\n{text[:10000]}\n\nTạo {n} câu hỏi."
    data = gpt_json(client, model, system, user, "ctu_question_set", GPT_QUESTION_SCHEMA)
    return data["questions"][:n]

def values_conflict(a, b):
    if isinstance(a, list): return sorted(map(str, a)) != sorted(map(str, b or []))
    if a in (None, "", []): return False
    if b in (None, "", []): return False
    return str(a).strip().lower() != str(b).strip().lower()


# ---------------------------------------------------------------------------
# Main

def dedupe_key(path):
    s = strip_accents(path.stem.lower()).replace("signed", "")
    return re.sub(r"[^a-z0-9]+", "", s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="raw/downloaded_files")
    ap.add_argument("--output", default="processed")
    ap.add_argument("--max-chars", type=int, default=1000)
    ap.add_argument("--min-chars", type=int, default=200)
    ap.add_argument("--overlap", type=int, default=120)
    ap.add_argument("--skip-forms", action="store_true")
    ap.add_argument("--gpt-metadata", action="store_true")
    ap.add_argument("--gpt-questions", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=0.4)
    args = ap.parse_args()

    inp, out = Path(args.input), Path(args.output)
    (out / "text").mkdir(parents=True, exist_ok=True)

    client = get_openai_client() if (args.gpt_metadata or args.gpt_questions) else None
    model = os.getenv("OPENAI_MODEL", "gpt-5")

    files = [p for p in inp.rglob("*") if p.is_file() and not p.name.startswith("~$") and p.suffix.lower() in (".docx", ".pdf", ".doc")]
    files.sort(key=lambda p: (p.suffix.lower() != ".docx", p.name.lower()))

    seen_key, seen_hash, report, qa_rows = {}, {}, [], []
    n_docs = n_chunks = 0

    with open(out / "documents.jsonl", "w", encoding="utf-8") as f_docs, \
         open(out / "chunks.jsonl", "w", encoding="utf-8") as f_chunks:
         
        for path in files:
            row = {"file": nfc(path.name), "status": "", "chars": 0, "pages": "", "doc_type": "", "ngay_ban_hanh": "", "khoa": "", "is_form": "", "duplicate_of": "", "chunks": ""}

            try:
                ext = path.suffix.lower()
                if ext == ".doc":
                    row["status"] = "bo_qua_.doc_cu (hay chuyen sang .docx)"
                    report.append(row)
                    continue

                key = dedupe_key(path)
                if key in seen_key:
                    row["status"] = "trung_ten"
                    row["duplicate_of"] = seen_key[key]
                    report.append(row)
                    continue

                # ----- BÓC TÁCH BẰNG DOCLING -----
                print(f"-> Đang xử lý: {path.name}")
                paras, n_pages, needs_ocr, full_md = read_document_docling(path)
                paras = clean_paras(paras)
                
                # Bản text sạch từ Docling
                full = full_md if full_md else "\n".join(p["text"] for p in paras)
                row["chars"], row["pages"] = len(full), n_pages or ""

                if len(full) < 50:
                    row["status"] = "can_kiem_tra (File rỗng hoặc lỗi bóc tách)"
                    report.append(row)
                    continue

                h = hashlib.md5(re.sub(r"\s+", "", full.lower()).encode()).hexdigest()
                if h in seen_hash:
                    row["status"] = "trung_noi_dung"
                    row["duplicate_of"] = seen_hash[h]
                    report.append(row)
                    continue

                seen_key[key], seen_hash[h] = row["file"], row["file"]

                # ----- TRÍCH XUẤT METADATA -----
                heuristic = extract_metadata(path, paras)
                final_meta = dict(heuristic)
                gpt_meta, review_required = None, False

                if args.gpt_metadata and client:
                    head = "\n".join(p["text"] for p in paras[:60])
                    try:
                        gpt_meta = gpt_enrich_metadata(client, model, path.name, heuristic, head)
                        for field in ("title", "doc_type", "so_hieu", "ngay_ban_hanh", "nam_hoc", "khoa", "is_form"):
                            if values_conflict(heuristic.get(field), gpt_meta.get(field)):
                                review_required = True
                        for field, value in gpt_meta.items():
                            if field not in ("confidence", "evidence", "topics") and (field not in final_meta or not final_meta[field]):
                                final_meta[field] = value
                    except Exception as ai_err:
                        print(f"   [Cảnh báo] Lỗi gọi API AI: {ai_err}")

                doc_id = sha1(row["file"])
                (out / "text" / f"{doc_id}.txt").write_text(full, encoding="utf-8")

                doc = {
                    "doc_id": doc_id, "source_file": row["file"], "format": ext[1:],
                    "pages": n_pages, "chars": len(full),
                    "metadata_method": "heuristic+ai" if gpt_meta else "heuristic",
                    "review_required": review_required,
                    "heuristic_metadata": heuristic, "gpt_metadata": gpt_meta,
                    **final_meta,
                }
                f_docs.write(json.dumps(doc, ensure_ascii=False) + "\n")
                n_docs += 1

                # ----- CHIA CHUNKS -----
                chunks = [] if (args.skip_forms and final_meta["is_form"]) else chunk_doc(paras, args.max_chars, args.min_chars, args.overlap)

                for i, c in enumerate(chunks):
                    ctx = final_meta["title"] + (f" — {c['section']}" if c["section"] else "")
                    rec = {
                        "chunk_id": f"{doc_id}_{i:03d}", "doc_id": doc_id, "source_file": row["file"],
                        "title": final_meta["title"], "doc_type": final_meta["doc_type"],
                        "so_hieu": final_meta["so_hieu"], "ngay_ban_hanh": final_meta["ngay_ban_hanh"],
                        "nam": final_meta["nam"], "nam_hoc": final_meta["nam_hoc"],
                        "khoa": final_meta["khoa"], "is_form": final_meta["is_form"],
                        "section": c["section"], "dieu": c["dieu"], "page": c["page"],
                        "text": c["text"], "text_with_context": f"{ctx}\n{c['text']}", "n_chars": len(c["text"]),
                    }
                    f_chunks.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n_chunks += 1

                    if args.gpt_questions > 0 and client:
                        try:
                            qs = gpt_generate_questions(client, model, final_meta["title"], c["section"], c["text"], args.gpt_questions)
                            for q in qs:
                                qa_rows.append({"question": q["question"], "intent": q["intent"], "answer_type": q["answer_type"], "doc_id": doc_id, "chunk_id": rec["chunk_id"], "source_file": row["file"], "title": final_meta["title"], "page": c["page"]})
                            time.sleep(args.sleep)
                        except Exception as ai_err:
                            pass

                row.update(status="ok", doc_type=final_meta["doc_type"], ngay_ban_hanh=final_meta["ngay_ban_hanh"] or "", khoa=",".join(final_meta["khoa"]), is_form=final_meta["is_form"], chunks=len(chunks))
                print(f"   [Thành công] {final_meta['doc_type']:12} | Tạo được {len(chunks):3} chunks")

            except Exception as e:
                row["status"] = f"loi: {e}"
                print(f"   [Lỗi hệ thống] {path.name}: {e}")

            report.append(row)

    # Xuất báo cáo CSV
    with open(out / "report.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(report[0].keys()) if report else ["file"])
        writer.writeheader()
        writer.writerows(report)

    # Xuất câu hỏi nếu có
    if qa_rows:
        with open(out / "gpt_questions.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(qa_rows[0].keys()))
            writer.writeheader()
            writer.writerows(qa_rows)

    status = Counter(r["status"].split(" ")[0].split(":")[0] for r in report)
    print(f"\n[HOÀN TẤT] Xử lý xong {n_docs} tài liệu, tạo được {n_chunks} chunk -> Xem tại thư mục '{out}/'")
    print("Thống kê trạng thái:", dict(status))

if __name__ == "__main__":
    main()