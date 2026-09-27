# 🤖 Chatbot Tư vấn Sinh viên — Đại học Cần Thơ

> **Môn học:** Nhập môn Công nghệ Số và Khoa học Máy tính (NLCSNKHMT)
> **Học kỳ:** HK1 2026–2027

---

## Giới thiệu

Chatbot RAG (Retrieval-Augmented Generation) hỗ trợ tư vấn thông tin cho sinh viên Trường Đại học Cần Thơ. Hệ thống trả lời các câu hỏi về:

- 📋 Đăng ký học phần & thời khóa biểu
- 💰 Học phí, miễn giảm, chính sách vay
- 🏠 Ký túc xá
- 🎓 Học bổng & công tác sinh viên
- 📖 Quy chế học vụ, đào tạo
- 📊 Điểm rèn luyện
- 🏫 Danh mục ngành & khoa
- 🤝 Đoàn – Hội

## Kiến trúc

```
Câu hỏi → Embedding (BGE-M3) → Hybrid Search (Vector + BM25 + RRF)
       → Top-K chunks → OpenAI GPT-4o-mini → Câu trả lời có nguồn
```

| Thành phần | Công nghệ |
|---|---|
| Embedding | `BAAI/bge-m3` (multilingual, 1024-dim) |
| Vector DB | ChromaDB (local, serverless) |
| Tìm kiếm | Hybrid: cosine similarity + BM25 + Reciprocal Rank Fusion |
| Sinh câu trả lời | OpenAI GPT-4o-mini |
| Dữ liệu | 14 tài liệu chính thức + 36 cặp FAQ |

## Cấu trúc dự án

```
chatbot-ctu-NLCSNKHMT/
├── Data_CTU_restructured/       # Kho dữ liệu
│   ├── raw/                     # Tài liệu gốc (PDF, DOCX) + metadata
│   ├── processed/               # Đã chuẩn hóa (.md)
│   └── faq/                     # FAQ theo chủ đề
│
├── rag_pipeline/                # Pipeline chính
│   ├── config.py                # Cấu hình trung tâm
│   ├── build_index.py           # Xây dựng cơ sở tri thức
│   ├── chunker.py               # Chia văn bản thành đoạn
│   ├── embedder.py              # Tạo embedding
│   ├── faq_parser.py            # Phân tích file FAQ
│   ├── metadata.py              # Đọc metadata .meta.json
│   ├── textutil.py              # Tiện ích xử lý text tiếng Việt
│   ├── search.py                # Tìm kiếm hybrid
│   ├── generate.py              # Sinh câu trả lời (GPT)
│   ├── eval_qa.py               # Đánh giá tự động
│   └── HUONG_DAN.md             # Hướng dẫn chi tiết
│
└── .gitignore
```

## Cài đặt & Chạy

### Yêu cầu
- Python 3.10+
- OpenAI API key

### Cài đặt
```bash
cd rag_pipeline
pip install -r requirements.txt
```

### Cấu hình
Tạo file `.env` ở thư mục gốc:
```
OPENAI_API_KEY=sk-proj-...
```

### Chạy
```bash
# 1. Xây dựng cơ sở tri thức (lần đầu tải BGE-M3 ~2GB)
python build_index.py --data-dir ../Data_CTU_restructured

# 2. Tìm kiếm thử
python search.py "học phí học kỳ 1 đóng khi nào?" -k 5

# 3. Hỏi-đáp tương tác (sinh câu trả lời bằng GPT)
python generate.py
```

> 💡 Xem thêm hướng dẫn chi tiết tại [`rag_pipeline/HUONG_DAN.md`](rag_pipeline/HUONG_DAN.md)

## Dữ liệu

Toàn bộ dữ liệu thu thập từ nguồn chính thức `*.ctu.edu.vn`. Xem chi tiết tại:
- [`Data_CTU_restructured/README.md`](Data_CTU_restructured/README.md)
- [`Data_CTU_restructured/THONG_KE_DU_LIEU.md`](Data_CTU_restructured/THONG_KE_DU_LIEU.md)
