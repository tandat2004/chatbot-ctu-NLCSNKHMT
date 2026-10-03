# -*- coding: utf-8 -*-
"""
Gom danh sách các file nguồn (source_files) DUY NHẤT từ file
ctu_chatbot_qa.csv (kết quả crawl từ crawl_ctu_chatbot.py).

Mục đích: có được danh mục văn bản gốc (PDF/docx) mà chatbot CTU
đang dùng làm nguồn RAG, để đi tìm/xin bản gốc về dùng cho đồ án.

CÁCH DÙNG:
    python list_source_files.py

Input:  ctu_chatbot_qa.csv  (cùng thư mục, hoặc sửa INPUT_CSV bên dưới)
Output: unique_source_files.csv  (danh sách file + các câu hỏi liên quan)
"""

import csv
import os
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(SCRIPT_DIR, "ctu_chatbot_qa.csv")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "unique_source_files.csv")


def main():
    # file_name -> list các câu hỏi đã trích dẫn tới file đó
    file_to_questions = defaultdict(list)

    if not os.path.exists(INPUT_CSV):
        print(f"KHÔNG TÌM THẤY file: {INPUT_CSV}")
        print("Hãy chắc chắn file ctu_chatbot_qa.csv nằm CÙNG THƯ MỤC với script này.")
        return

    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get("question", "").strip()
            sources_raw = row.get("source_files", "").strip()
            if not sources_raw:
                continue
            # source_files được lưu dạng "file1.pdf; file2.docx; ..."
            for fname in sources_raw.split(";"):
                fname = fname.strip()
                if fname and not fname.startswith("ERROR"):
                    file_to_questions[fname].append(question)

    # Sắp xếp theo tên file cho dễ nhìn
    unique_files = sorted(file_to_questions.keys())

    print(f"Tổng số file nguồn DUY NHẤT: {len(unique_files)}\n")
    for fname in unique_files:
        print(f"- {fname}  (xuất hiện trong {len(file_to_questions[fname])} câu hỏi)")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "so_lan_xuat_hien", "cac_cau_hoi_lien_quan"])
        for fname in unique_files:
            qs = file_to_questions[fname]
            writer.writerow([fname, len(qs), " | ".join(qs)])

    print(f"\nĐã lưu danh sách chi tiết vào {OUTPUT_CSV}")


if __name__ == "__main__":
    main()