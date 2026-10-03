#!/usr/bin/env python3
"""
generate_question_bank.py
Sinh ngân hàng câu hỏi khai thác chatbot bằng OpenAI Structured Outputs.

Mục tiêu:
- Không viết tay toàn bộ hàng nghìn câu hỏi.
- GPT tạo câu hỏi đa dạng theo từng chủ đề.
- Mỗi câu có intent/answer_type để phân tích coverage.
- Loại trùng exact sau khi sinh.

Chạy:
    pip install openai
    set OPENAI_API_KEY=...
    set OPENAI_MODEL=gpt-5
    python generate_question_bank.py --per-category 30

Có thể sửa CATEGORIES để khớp phạm vi niên luận.
"""

import argparse
import csv
import json
import os
import re
import unicodedata
from pathlib import Path

from openai import OpenAI


CATEGORIES = {
    "nhap_hoc": [
        "hồ sơ nhập học", "quy trình nhập học", "thời hạn",
        "thiếu hồ sơ", "nhập học trực tuyến", "xác nhận nhập học",
        "thông tin cá nhân", "giấy khám sức khỏe",
    ],
    "hoc_phi": [
        "mức học phí", "theo tín chỉ", "học lại", "học cải thiện",
        "rút học phần", "hoàn học phí", "hạn đóng", "phương thức thanh toán",
        "miễn giảm", "gia hạn", "nợ học phí",
    ],
    "hoc_vu": [
        "đăng ký học phần", "học phần tiên quyết", "rút học phần",
        "học lại", "học cải thiện", "bảo lưu", "thôi học",
        "chuyển ngành", "hai ngành", "cảnh báo học vụ",
    ],
    "diem": [
        "điểm học phần", "điểm chữ", "điểm trung bình",
        "phúc khảo", "thi lại", "thi bù", "điều kiện dự thi",
    ],
    "diem_ren_luyen": [
        "khái niệm", "cách tính", "tiêu chí", "cộng điểm",
        "trừ điểm", "khiếu nại", "ảnh hưởng học bổng", "xếp loại",
    ],
    "ky_tuc_xa": [
        "đối tượng", "điều kiện", "hồ sơ", "đăng ký",
        "giá phòng", "điện nước", "đổi phòng", "trả phòng",
        "nội quy", "giờ đóng mở cổng",
    ],
    "tai_khoan_dich_vu_so": [
        "tài khoản sinh viên", "email", "MyCTU", "mật khẩu",
        "wifi", "thời khóa biểu", "điểm", "lịch thi", "dịch vụ trực tuyến",
    ],
    "bhyt": [
        "bắt buộc", "mức đóng", "thời hạn", "đăng ký",
        "nơi khám chữa bệnh ban đầu", "thẻ điện tử", "mất thẻ",
    ],
    "hoc_bong_tai_chinh": [
        "học bổng khuyến khích", "học bổng doanh nghiệp",
        "hoàn cảnh khó khăn", "miễn giảm học phí", "vay vốn",
        "hồ sơ", "thời hạn", "điều kiện",
    ],
    "doan_hoi_clb": [
        "Đoàn", "Hội Sinh viên", "câu lạc bộ",
        "tình nguyện", "phong trào", "điểm rèn luyện",
    ],
    "thu_vien_hoc_lieu": [
        "thư viện", "mượn sách", "trả sách", "tài liệu điện tử",
        "cơ sở dữ liệu học thuật", "phòng tự học",
    ],
    "quyen_nghia_vu_ky_luat": [
        "quyền sinh viên", "nghĩa vụ", "nội quy",
        "hành vi bị cấm", "kỷ luật", "khiếu nại",
    ],
    "tot_nghiep": [
        "điều kiện tốt nghiệp", "tín chỉ", "ngoại ngữ",
        "giáo dục thể chất", "giáo dục quốc phòng", "xét tốt nghiệp",
        "thực tập", "khóa luận", "đồ án",
    ],
    "truy_nguon": [
        "tên văn bản", "số hiệu", "ngày ban hành", "đơn vị ban hành",
        "hiệu lực", "văn bản thay thế", "văn bản sửa đổi",
        "tài liệu tham khảo", "trang tài liệu", "file PDF",
    ],
}


SCHEMA = {
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
                    "intent": {
                        "type": "string",
                        "enum": [
                            "definition", "condition", "procedure", "deadline",
                            "fee", "document", "authority", "exception",
                            "source", "comparison", "scenario", "overview"
                        ],
                    },
                    "answer_type": {
                        "type": "string",
                        "enum": [
                            "fact", "procedure", "list", "condition",
                            "deadline", "calculation", "scenario"
                        ],
                    },
                    "target": {"type": "string"},
                },
                "required": ["question", "intent", "answer_type", "target"],
            },
        }
    },
    "required": ["questions"],
}


def normalize(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
    return s.strip()


def ask_gpt(client, model, category, dimensions, n):
    system = """Bạn thiết kế bộ câu hỏi kiểm thử cho chatbot tân sinh viên.
Bối cảnh: Đại học Cần Thơ.
Mỗi câu phải tự nhiên như câu hỏi thực tế của sinh viên.
Tập trung vào thông tin hành chính/học vụ/dịch vụ sinh viên.
Không được tự thêm số liệu, tên văn bản, mức phí hoặc thời hạn cụ thể
nếu không có trong chủ đề; câu hỏi có thể hỏi "bao nhiêu", "khi nào",
"ở đâu" mà không chứa câu trả lời.
Tạo coverage đa dạng: định nghĩa, điều kiện, thủ tục, hồ sơ, thời hạn,
đối tượng, ngoại lệ, tình huống, nơi liên hệ và truy nguồn.
Không tạo câu hỏi chỉ khác một vài từ.
Mục tiêu là phát hiện tài liệu nguồn, không phải kiểm tra khả năng sáng tạo."""
    user = f"""Chủ đề: {category}
Các khía cạnh cần phủ:
{json.dumps(dimensions, ensure_ascii=False)}

Hãy tạo {n} câu hỏi đa dạng."""
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ctu_question_bank",
                "schema": SCHEMA,
                "strict": True,
            }
        },
    )
    return json.loads(response.output_text)["questions"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-category", type=int, default=30)
    ap.add_argument("--output", default="question_bank")
    args = ap.parse_args()

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("Thiếu OPENAI_API_KEY.")
    model = os.getenv("OPENAI_MODEL", "gpt-5")
    client = OpenAI(api_key=key)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    seen = set()

    for category, dims in CATEGORIES.items():
        print(f"[GPT] {category}")
        items = ask_gpt(client, model, category, dims, args.per_category)

        for item in items:
            q = item["question"].strip()
            key_q = normalize(q)
            if not q or key_q in seen:
                continue
            seen.add(key_q)
            rows.append({
                "category": category,
                "question": q,
                "intent": item["intent"],
                "answer_type": item["answer_type"],
                "target": item["target"],
            })

    jsonl = out / "questions.jsonl"
    with open(jsonl, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    csv_path = out / "questions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["question"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nTổng: {len(rows)} câu")
    print(f"CSV : {csv_path}")
    print(f"JSONL: {jsonl}")


if __name__ == "__main__":
    main()
