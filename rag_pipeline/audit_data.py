import os
import json
import pandas as pd

# Các đường dẫn file dữ liệu (thay đổi nếu bạn lưu ở thư mục khác)
DOCS_FILE = "data/2_processed/documents.jsonl"
CHUNKS_FILE = "data/2_processed/chunks.jsonl"
QUESTIONS_FILE = "data/3_faq/ctu_chatbot_qa.csv" # Hoặc thay bằng "question_bank/questions.csv" nếu bạn dùng file khác

def load_jsonl(filepath):
    data = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line.strip()))
    return pd.DataFrame(data)

def main():
    print("="*50)
    print(" BÁO CÁO KIỂM TOÁN DỮ LIỆU RAG (DATA AUDIT)")
    print("="*50)

    # 1. AUDIT TÀI LIỆU (DOCUMENTS)
    df_docs = load_jsonl(DOCS_FILE)
    if not df_docs.empty:
        print(f"\n[1] TỔNG QUAN TÀI LIỆU: {len(df_docs)} file gốc")
        print("-" * 30)
        print("Phân loại tài liệu (doc_type):")
        print(df_docs['doc_type'].value_counts().to_string())
        
        review_count = df_docs['review_required'].sum() if 'review_required' in df_docs.columns else 0
        if review_count > 0:
            print(f"\n⚠️ CẢNH BÁO: Có {review_count} tài liệu bị xung đột siêu dữ liệu (cần người kiểm tra lại).")
    else:
        print("\n[1] Không tìm thấy file documents.jsonl")

    # 2. AUDIT ĐOẠN TRI THỨC (CHUNKS)
    df_chunks = load_jsonl(CHUNKS_FILE)
    if not df_chunks.empty:
        print(f"\n[2] TỔNG QUAN TRI THỨC (CHUNKS): {len(df_chunks)} đoạn")
        print("-" * 30)
        avg_len = df_chunks['n_chars'].mean()
        print(f"Chiều dài trung bình mỗi chunk: {avg_len:.0f} ký tự")
        
        if avg_len < 200:
            print("⚠️ LƯU Ý: Chunks đang khá ngắn, chatbot có thể thiếu ngữ cảnh khi trả lời.")
        elif avg_len > 1000:
            print("⚠️ LƯU Ý: Chunks khá dài, có thể gây nhiễu cho mô hình AI.")
    else:
        print("\n[2] Không tìm thấy file chunks.jsonl")

    # 3. AUDIT NGÂN HÀNG CÂU HỎI (FAQs) & ĐỘ PHỦ (COVERAGE)
    if os.path.exists(QUESTIONS_FILE):
        df_qa = pd.read_csv(QUESTIONS_FILE, encoding="utf-8-sig")
        print(f"\n[3] TỔNG QUAN CÂU HỎI (FAQs): {len(df_qa)} câu")
        print("-" * 30)
        
        # Thống kê theo mục đích hỏi (Intent) nếu có
        if 'intent' in df_qa.columns:
            print("Phân bố câu hỏi theo mục đích (Intent):")
            print(df_qa['intent'].value_counts().to_string())
            print()
            
        # Kiểm tra tỷ lệ Chunk / Câu hỏi
        if not df_chunks.empty:
            ratio = len(df_qa) / len(df_chunks)
            print(f"Tỷ lệ Câu hỏi / Đoạn tri thức: {ratio:.2f}")
            if ratio < 0.5:
                print("❌ ĐÁNH GIÁ: THIẾU CÂU HỎI. Số lượng FAQ đang ít hơn 50% số chunk tài liệu.")
                print("   -> Lời khuyên: Chạy thêm kịch bản sinh câu hỏi để đa dạng hóa góc hỏi, hoặc bổ sung các câu hỏi thủ công (ví dụ: xin chào, cảm ơn) mà tài liệu không có.")
            elif ratio > 3.0:
                print("⚠️ LƯU Ý: Dư thừa câu hỏi. Nhiều câu hỏi đang trỏ vào cùng 1 chunk, cẩn thận trùng lặp nội dung.")
            else:
                print("✅ ĐÁNH GIÁ: Tỷ lệ phủ câu hỏi TỐT (đủ để test mô hình).")
    else:
        print(f"\n[3] Không tìm thấy file FAQ ({QUESTIONS_FILE}).")
        print("❌ ĐÁNH GIÁ: CHƯA CÓ CÂU HỎI. Bạn cần chạy script sinh câu hỏi để tạo tập test/FAQ.")

    print("\n" + "="*50)

if __name__ == "__main__":
    main()