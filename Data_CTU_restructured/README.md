# 📚 Data_CTU_restructured — Kho dữ liệu RAG Trợ lý Sinh viên CTU

> Cập nhật: 2026-09-11 | Phiên bản: 1.0

---

## Mục tiêu

Cung cấp tài liệu chính thức, có cấu trúc cho hệ thống RAG (Retrieval-Augmented Generation)
phục vụ chatbot tư vấn sinh viên Trường Đại học Cần Thơ.

---

## Cấu trúc thư mục

```
Data_CTU_restructured/
├── raw/                     # File gốc chưa xử lý (PDF, Word, MD)
│   ├── handbook/            # Sổ tay sinh viên
│   ├── hoc_vu/              # Quy định học vụ, đào tạo
│   ├── dang_ky_hoc_phan/    # Kế hoạch đăng ký học phần
│   ├── hoc_phi/             # Học phí, miễn giảm, chính sách vay
│   ├── ktx/                 # Ký túc xá
│   ├── hoc_bong_ctsv/       # Học bổng, công tác sinh viên, rèn luyện
│   ├── danh_muc_nganh/      # Khoa & ngành đào tạo
│   ├── doan_hoi/            # Đoàn - Hội (nguồn web)
│   └── tham_khao/           # Tài liệu tham khảo khác
│
├── processed/               # File đã chuẩn hóa (.md / .txt) — dùng để index RAG
│   ├── handbook/
│   ├── hoc_vu/
│   ├── dang_ky_hoc_phan/
│   ├── hoc_phi/
│   ├── ktx/
│   ├── hoc_bong_ctsv/
│   └── danh_muc_nganh/
│
└── faq/                     # Bảng câu hỏi - trả lời chuẩn
    ├── faq_template.md      # Template soạn FAQ
    └── faq_hoc_phi.md       # (ví dụ) FAQ theo chủ đề
```

---

## Quy tắc thu thập dữ liệu

| Tiêu chí | Yêu cầu |
|---|---|
| **Nguồn** | Ưu tiên tuyệt đối: website `.ctu.edu.vn`, văn bản có số hiệu/dấu |
| **Tính pháp lý** | Không dùng group/fanpage không chính thống làm *nội dung trả lời* |
| **Versioning** | Ghi rõ ngày hiệu lực trong metadata mỗi file |
| **Định dạng raw** | Giữ nguyên file gốc, không chỉnh sửa |
| **Định dạng processed** | Chuẩn hóa sang `.md` với heading rõ ràng để chunk dễ |

---

## Metadata bắt buộc cho mỗi file raw

Tạo file `<ten_file>.meta.json` đặt cùng thư mục với file gốc:

```json
{
  "filename": "Ten_file.pdf",
  "topic": "hoc_phi",
  "so_hieu": "QD số.../năm/QĐ-ĐHCT",
  "tieu_de": "Tên đầy đủ của văn bản",
  "source_url": "https://...",
  "cap_ban_hanh": "Trường ĐHCT / Bộ GD&ĐT / Thủ tướng",
  "hieu_luc_tu": "YYYY-MM-DD",
  "hieu_luc_den": "YYYY-MM-DD hoặc null nếu chưa hết hạn",
  "hoc_ky_ap_dung": "HK1 2026-2027",
  "kiem_tra_lai_vao": "YYYY-MM-DD",
  "ghi_chu": ""
}
```

---

## Trạng thái hiện tại (2026-09-11)

| Thư mục | Raw | Processed | FAQ |
|---|---|---|---|
| handbook | ✅ 1 file | ⬜ Chưa | ⬜ Chưa |
| hoc_vu | ✅ 4 files | ⬜ Chưa | ⬜ Chưa |
| dang_ky_hoc_phan | ✅ 1 file | ⬜ Chưa | ⬜ Chưa |
| hoc_phi | ✅ 4 files | ⬜ Chưa | ⬜ Chưa |
| ktx | ✅ 2 files | ⬜ Chưa | ⬜ Chưa |
| hoc_bong_ctsv | ✅ 2 files | ⬜ Chưa | ⬜ Chưa |
| danh_muc_nganh | ✅ 1 file | ⬜ Chưa | ⬜ Chưa |
| doan_hoi | 🔗 Web source | ⬜ Chưa | ⬜ Chưa |

---

## Bước tiếp theo

1. [ ] Tạo `.meta.json` cho từng file trong `raw/`
2. [ ] Chuyển đổi PDF → `.md` vào `processed/` (dùng tool OCR/PDF parser)
3. [ ] Xây dựng bảng FAQ theo từng chủ đề trong `faq/`
4. [ ] Thu thập dữ liệu Đoàn - Hội từ nguồn web chính thức
5. [ ] Index vào vector database (ChromaDB / Pinecone / FAISS)
