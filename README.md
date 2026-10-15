# CTU Chatbot RAG - Trợ Lý Tư Vấn Học Vụ & Đời Sống Sinh Viên ĐH Cần Thơ

> **Đề tài:** Xây dựng Chatbot tư vấn quy chế, học vụ và đời sống sinh viên Trường Đại học Cần Thơ ứng dụng RAG (Retrieval-Augmented Generation)  
> **Học phần:** Niên luận cơ sở ngành Khoa học máy tính (NLCSNKHMT)  
> **Trường:** Trường Công nghệ Thông tin & Truyền thông – Trường Đại học Cần Thơ (CTU)

---

## 📌 Báo cáo tiến độ & Danh mục tài liệu
* 📑 **Báo cáo chi tiết tiến độ & kết quả dữ liệu:** 👉 [Xem file BAO_CAO_TIEN_DO_DU_LIEU.md](./BAO_CAO_TIEN_DO_DU_LIEU.md)
* 📚 **Danh mục chi tiết 97 tài liệu hiện có trong hệ thống:** 👉 [Xem file DANH_MUC_TAI_LIEU.md](./DANH_MUC_TAI_LIEU.md)

---

## 📊 Tóm tắt số liệu nổi bật

* **Tài liệu nguồn thu thập:** **96 tệp tin** (PDF, DOCX, XLSX, TXT)
* **Tài liệu chuẩn hóa đưa vào RAG:** **88 văn bản** chính quy (Quy chế học vụ 3266, 40 biểu mẫu đơn từ, học phí, học bổng, KTX,...)
* **Số ký tự trích xuất:** **671.593 ký tự** (~156 trang văn bản)
* **Số đoạn tri thức (Chunks):** **670 chunks** (chiều dài trung bình: **754 ký tự/chunk**)
* **Ngân hàng câu hỏi (FAQ Bank):** **474 câu hỏi - đáp** thực tế từ sinh viên CTU và biểu mẫu học vụ
* **Độ phủ câu hỏi / Chunk:** **0.68** (Đạt chuẩn TỐT)
* **Cơ sở dữ liệu Vector:** **ChromaDB** với **1.113 vectors** (nhúng bằng mô hình `BAAI/bge-m3`)
* **Kiến trúc sinh:** Hỗ trợ đa nhà cung cấp LLM (OpenAI, Google Gemini, Groq LLaMA 3) kèm System Prompt chống ảo giác và trích dẫn số nguồn minh bạch.

---

## 🛠️ Cấu trúc thư mục

```text
chatbot-ctu-NLCSNKHMT/
├── README.md                     # Giới thiệu dự án
├── index.html                    # Giao diện Web Trợ lý Học vụ CTU
├── rag_pipeline/                 # Thư mục chính phục vụ Chatbot & RAG (được đẩy lên Git)
│   ├── api.py                    # FastAPI server cung cấp endpoint /chat
│   ├── generate.py               # Module truy hồi ChromaDB và sinh câu trả lời RAG
│   ├── build_vector_db.py        # Script nhúng chunks + FAQ vào ChromaDB (BAAI/bge-m3)
│   └── requirements.txt          # Danh sách thư viện cần thiết cho RAG Chatbot
├── data_pipeline/                # Quá trình thu thập & lọc dữ liệu (đã ignore trên Git)
│   ├── crawl.py                  # Thu thập Q&A mẫu từ hệ thống K52 Buddy
│   ├── download_source_files.py  # Tải văn bản nguồn gốc tự động
│   ├── process_docs_gpt.py       # Tiền xử lý tài liệu đa định dạng bằng IBM Docling
│   ├── generate_question_bank.py # Sinh ngân hàng câu hỏi thử nghiệm bằng LLM
│   ├── list_source.py            # Lọc danh mục các tài liệu nguồn
│   ├── audit_data.py             # Kiểm toán chất lượng và độ phủ dữ liệu
│   └── data/                     # Thư mục dữ liệu (1_raw, 2_processed, 3_faq)
└── db/
    └── chroma_db/                # Cơ sở dữ liệu Vector ChromaDB (1.113 vectors)
```

---

## 🚀 Hướng dẫn chạy thử nghiệm

### 1. Cài đặt thư viện
```bash
cd rag_pipeline
pip install -r requirements.txt
```

### 2. Khởi tạo / Cập nhật Vector Database

* **Cách A: Thêm / Cập nhật nhanh 1 tài liệu mới (Khuyên dùng):**
  ```bash
  python ingest_file.py "data_pipeline/data/1_raw/ten_file_moi.pdf"
  ```
  *(Tự động trích xuất bảng biểu bằng Docling, cắt chunk, nhúng vector vào ChromaDB chỉ trong 15-20 giây).*

* **Cách B: Xây dựng lại toàn bộ Vector DB từ đầu (Tất cả tài liệu + FAQ):**
  ```bash
  cd rag_pipeline
  python build_vector_db.py
  ```

### 3. Khởi chạy API Server
```bash
cd rag_pipeline
python api.py
```
Server chạy tại `http://127.0.0.1:8000`.

### 4. Mở giao diện Web
Mở trực tiếp file [index.html](./index.html) trên trình duyệt hoặc chạy qua Live Server để tương tác với Chatbot.

