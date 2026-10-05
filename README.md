# CTU Chatbot RAG - Trợ Lý Tư Vấn Học Vụ & Đời Sống Sinh Viên ĐH Cần Thơ

> **Đề tài:** Xây dựng Chatbot tư vấn quy chế, học vụ và đời sống sinh viên Trường Đại học Cần Thơ ứng dụng RAG (Retrieval-Augmented Generation)  
> **Học phần:** Niên luận cơ sở ngành Khoa học máy tính (NLCSNKHMT)  
> **Trường:** Trường Công nghệ Thông tin & Truyền thông – Trường Đại học Cần Thơ (CTU)

---

## 📌 Báo cáo tiến độ & Dữ liệu
* 📑 **Báo cáo chi tiết tiến độ, số lượng & kết quả dữ liệu:** 👉 [Xem file BAO_CAO_TIEN_DO_DU_LIEU.md](./BAO_CAO_TIEN_DO_DU_LIEU.md)

---

## 📊 Tóm tắt số liệu nổi bật

* **Tài liệu nguồn thu thập:** **96 tệp tin** (PDF, DOCX, XLSX, TXT)
* **Tài liệu chuẩn hóa đưa vào RAG:** **88 văn bản** chính quy (Quy chế học vụ 3266, 40 biểu mẫu đơn từ, học phí, học bổng, KTX,...)
* **Số ký tự trích xuất:** **671.593 ký tự** (~156 trang văn bản)
* **Số đoạn tri thức (Chunks):** **670 chunks** (chiều dài trung bình: **754 ký tự/chunk**)
* **Ngân hàng câu hỏi (FAQ Bank):** **443 câu hỏi - đáp** thực tế từ K52 Buddy Chatbot
* **Độ phủ câu hỏi / Chunk:** **0.66** (Đạt chuẩn TỐT)
* **Cơ sở dữ liệu Vector:** **ChromaDB** với **1.113 vectors** (nhúng bằng mô hình `BAAI/bge-m3`)
* **Kiến trúc sinh:** Hỗ trợ đa nhà cung cấp LLM (OpenAI, Google Gemini, Groq LLaMA 3) kèm System Prompt chống ảo giác và trích dẫn số nguồn minh bạch.

---

## 🛠️ Cấu trúc thư mục

```text
chatbot-ctu-NLCSNKHMT/
├── BAO_CAO_TIEN_DO_DU_LIEU.md    # Báo cáo chi tiết tiến độ và kết quả dữ liệu gửi Thầy
├── README.md                     # Giới thiệu dự án
├── index.html                    # Giao diện Web Trợ lý Học vụ CTU
├── rag_pipeline/
│   ├── api.py                    # FastAPI server cung cấp endpoint /chat
│   ├── generate.py               # Module truy hồi ChromaDB và sinh câu trả lời RAG
│   ├── build_vector_db.py        # Script nhúng chunks + FAQ vào ChromaDB (BAAI/bge-m3)
│   ├── audit_data.py             # Script kiểm toán chất lượng và độ phủ dữ liệu
│   ├── crawl.py                  # Công cụ thu thập Q&A mẫu từ hệ thống K52 Buddy
│   ├── download_source_files.py  # Công cụ tải văn bản nguồn gốc tự động
│   ├── process_docs_gpt.py       # Tiền xử lý tài liệu đa định dạng bằng IBM Docling
│   └── data/
│       ├── 1_raw/                # 96 tệp tài liệu gốc thu thập từ CTU
│       ├── 2_processed/          # documents.jsonl, chunks.jsonl, report.csv
│       └── 3_faq/                # ctu_chatbot_qa.csv (443 cặp hỏi đáp)
└── db/
    └── chroma_db/                # Cơ sở dữ liệu Vector ChromaDB (1.113 vectors)
```

---

## 🚀 Hướng dẫn chạy thử nghiệm

### 1. Cài đặt thư viện
```bash
cd rag_pipeline
pip install -r requirements_gpt.txt
pip install fastapi uvicorn chromadb python-dotenv
```

### 2. Kiểm toán dữ liệu
```bash
python audit_data.py
```

### 3. Khởi chạy API Server
```bash
python api.py
```
Server chạy tại `http://127.0.0.1:8000`.

### 4. Mở giao diện Web
Mở trực tiếp file [index.html](./index.html) trên trình duyệt hoặc chạy qua Live Server để tương tác với Chatbot.
