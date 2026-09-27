# 📊 Thống kê Dữ liệu — Chatbot Tư vấn Sinh viên CTU

> **Cập nhật:** 2026-09-24 | **Phiên bản dữ liệu:** 1.2

---

## 1. Tổng quan

| Hạng mục | Số lượng | Tổng dung lượng |
|---|---|---|
| **File raw** (tài liệu gốc) | 14 file | ~62.9 MB |
| **File metadata** (`.meta.json`) | 14 file | ~11 KB |
| **File processed** (đã chuẩn hóa `.md`) | 15 file | ~294.9 KB |
| **File FAQ** (câu hỏi – trả lời) | 8 chủ đề | ~110.3 KB |
| **Cặp câu hỏi – trả lời FAQ (có ID)** | **36 cặp** | — |
| **Bảng FAQ CSV (CTU_FAQ.csv)** | 56 hàng | ~35 KB |

---

## 2. Chi tiết theo chủ đề (Category)

| # | Chủ đề | Thư mục | Raw | Dung lượng Raw | Processed | Dung lượng Processed | FAQ file | Số câu FAQ |
|---|---|---|---|---|---|---|---|---|
| 1 | **Sổ tay sinh viên** | `handbook/` | `So_tay_sinh_vien_2025.pdf` | 796 KB | `So_tay_sinh_vien_2025.md` | 8.6 KB | `faq_handbook.md` | 5 |
| 2 | **Học vụ** | `hoc_vu/` | `QD3266_Quy_dinh_cong_tac_hoc_vu.pdf` | 22,115 KB | `QD3266_Quy_dinh_cong_tac_hoc_vu.md` | 64.5 KB | `faq_hoc_vu.md` | 4 |
| | | | `Quy_dinh_dao_tao_truc_tuyen.pdf` | 13,297 KB | `Quy_dinh_dao_tao_truc_tuyen.md` | 38.6 KB | | |
| | | | `Quy_dinh_mien_cong_nhan_diem.pdf` | 19,096 KB | `Quy_dinh_mien_cong_nhan_diem.md` | 49.2 KB | | |
| 3 | **Đăng ký học phần** | `dang_ky_hoc_phan/` | `Ke_hoach_dang_ky_hoc_phan_HK1_2026_2027.pdf` | 710 KB | `Ke_hoach_dang_ky_hoc_phan_HK1_2026_2027.md` | 7.2 KB | `faq_dang_ky_hoc_phan.md` | 4 |
| 4 | **Học phí** | `hoc_phi/` | `Muc_hoc_phi_2026_2027.pdf` | 695 KB | `Muc_hoc_phi_2026_2027.md` | 7.7 KB | `faq_hoc_phi.md` | 4 |
| | | | `QD05_2022_TTg.pdf` | 836 KB | `QD05_2022_TTg.md` | 6.1 KB | | |
| | | | `QD09_2022_TTg.pdf` | 458 KB | `QD09_2022_TTg.md` | 16.9 KB | | |
| | | | `Thong_bao_mien_giam_HK1_2026_2027.pdf` | 602 KB | `Thong_bao_mien_giam_HK1_2026_2027.md` | 8.3 KB | | |
| | | | *(FAQ tổng hợp học phí)* | — | `FAQ_hoc_phi.md` | 2.5 KB | | |
| 5 | **Ký túc xá** | `ktx/` | `Thong_bao_dang_ky_KTX_HK1_2026_2027.pdf` | 731 KB | `Thong_bao_dang_ky_KTX_HK1_2026_2027.md` | 7.7 KB | `faq_ktx.md` | 5 |
| 6 | **Học bổng & CTSV** | `hoc_bong_ctsv/` | `Cong_tac_sinh_vien.pdf` | 1,527 KB | `Cong_tac_sinh_vien.md` | 43.6 KB | `faq_hoc_bong_ctsv.md` | 4 |
| 7 | **Điểm rèn luyện** | `diem_ren_luyen/` | `Quy_che_diem_ren_luyen.pdf` | 3,523 KB | `Quy_che_diem_ren_luyen.md` | 20.4 KB | *(nằm trong hoc_bong_ctsv)* | — |
| 8 | **Danh mục ngành** | `danh_muc_nganh/` | `danh_muc_nganh.docx` | 16 KB | `danh_muc_nganh.md` | 5.2 KB | `faq_danh_muc_nganh.md` | 5 |
| 9 | **Đoàn – Hội** | `doan_hoi/` | `DOAN_HOI_WEB_SOURCES.md` *(web source)* | 5.7 KB | `doan_hoi_tong_hop.md` | 8.5 KB | `faq_doan_hoi.md` | 5 |

---

## 3. Chi tiết file Raw

### 3.1 Phân loại theo định dạng

| Định dạng | Số file | Dung lượng |
|---|---|---|
| `.pdf` | 12 | ~62.9 MB |
| `.docx` | 1 | ~16 KB |
| `.md` *(web source)* | 1 | ~5.7 KB |

### 3.2 Danh sách đầy đủ file Raw (không tính meta)

| Chủ đề | Tên file | Dung lượng |
|---|---|---|
| dang_ky_hoc_phan | `Ke_hoach_dang_ky_hoc_phan_HK1_2026_2027.pdf` | 710.1 KB |
| danh_muc_nganh | `danh_muc_nganh.docx` | 15.8 KB |
| diem_ren_luyen | `Quy_che_diem_ren_luyen.pdf` | 3,523.0 KB |
| doan_hoi | `DOAN_HOI_WEB_SOURCES.md` | 5.7 KB |
| handbook | `So_tay_sinh_vien_2025.pdf` | 796.2 KB |
| hoc_bong_ctsv | `Cong_tac_sinh_vien.pdf` | 1,527.3 KB |
| hoc_phi | `Muc_hoc_phi_2026_2027.pdf` | 695.4 KB |
| hoc_phi | `QD05_2022_TTg.pdf` | 836.0 KB |
| hoc_phi | `QD09_2022_TTg.pdf` | 458.2 KB |
| hoc_phi | `Thong_bao_mien_giam_HK1_2026_2027.pdf` | 602.4 KB |
| hoc_vu | `QD3266_Quy_dinh_cong_tac_hoc_vu.pdf` | 22,114.5 KB |
| hoc_vu | `Quy_dinh_dao_tao_truc_tuyen.pdf` | 13,296.6 KB |
| hoc_vu | `Quy_dinh_mien_cong_nhan_diem.pdf` | 19,095.9 KB |
| ktx | `Thong_bao_dang_ky_KTX_HK1_2026_2027.pdf` | 730.7 KB |

---

## 4. Chi tiết file Processed

| Chủ đề | Tên file (.md) | Dung lượng |
|---|---|---|
| dang_ky_hoc_phan | `Ke_hoach_dang_ky_hoc_phan_HK1_2026_2027.md` | 7.2 KB |
| danh_muc_nganh | `danh_muc_nganh.md` | 5.2 KB |
| diem_ren_luyen | `Quy_che_diem_ren_luyen.md` | 20.4 KB |
| doan_hoi | `doan_hoi_tong_hop.md` | 8.5 KB |
| handbook | `So_tay_sinh_vien_2025.md` | 8.6 KB |
| hoc_bong_ctsv | `Cong_tac_sinh_vien.md` | 43.6 KB |
| hoc_phi | `FAQ_hoc_phi.md` | 2.5 KB |
| hoc_phi | `Muc_hoc_phi_2026_2027.md` | 7.7 KB |
| hoc_phi | `QD05_2022_TTg.md` | 6.1 KB |
| hoc_phi | `QD09_2022_TTg.md` | 16.9 KB |
| hoc_phi | `Thong_bao_mien_giam_HK1_2026_2027.md` | 8.3 KB |
| hoc_vu | `QD3266_Quy_dinh_cong_tac_hoc_vu.md` | 64.5 KB |
| hoc_vu | `Quy_dinh_dao_tao_truc_tuyen.md` | 38.6 KB |
| hoc_vu | `Quy_dinh_mien_cong_nhan_diem.md` | 49.2 KB |
| ktx | `Thong_bao_dang_ky_KTX_HK1_2026_2027.md` | 7.7 KB |

---

## 5. Chi tiết FAQ

### 5.1 FAQ có cấu trúc ID (faq_*.md)

| File FAQ | Chủ đề | Số cặp Q&A |
|---|---|---|
| `faq_handbook.md` | Sổ tay sinh viên | 5 |
| `faq_hoc_vu.md` | Học vụ | 4 |
| `faq_dang_ky_hoc_phan.md` | Đăng ký học phần | 4 |
| `faq_hoc_phi.md` | Học phí | 4 |
| `faq_ktx.md` | Ký túc xá | 5 |
| `faq_hoc_bong_ctsv.md` | Học bổng & CTSV | 4 |
| `faq_danh_muc_nganh.md` | Danh mục ngành | 5 |
| `faq_doan_hoi.md` | Đoàn – Hội | 5 |
| **Tổng** | — | **36 cặp** |

### 5.2 Bảng FAQ CSV (CTU_FAQ.csv)

| Thuộc tính | Giá trị |
|---|---|
| Tổng số hàng | 56 hàng |
| Các cột | Câu hỏi mẫu, Chủ đề, Intent, Từ khóa, Câu trả lời, Nguồn, URL nguồn, Số biến thể |
| Dung lượng | ~35 KB |

### 5.3 Tài liệu FAQ bổ sung

| File | Mô tả | Dung lượng |
|---|---|---|
| `FAQ-Phong-CTSV-CTU.md` | FAQ Phòng Công tác Sinh viên | 6.8 KB |
| `bao_cao_khao_sat.md` | Báo cáo khảo sát nhu cầu tân sinh viên | 8.4 KB |
| `KHẢO SÁT NHU CẦU...csv` | Dữ liệu khảo sát gốc | 13.2 KB |

---

## 6. Tổng hợp nhanh

```
Data_CTU_restructured/
├── raw/           14 file gốc     ~62.9 MB  (9 thư mục chủ đề)
│                  14 meta.json    ~11 KB
├── processed/     15 file .md     ~294.9 KB (9 thư mục chủ đề)
└── faq/           13 file         ~110.3 KB
                    ├── 8 file FAQ có ID  → 36 cặp Q&A
                    ├── CTU_FAQ.csv       → 56 hàng
                    └── file bổ sung khác
```

---

## 7. Trạng thái hoàn thành

| Chủ đề | Raw | Metadata | Processed | FAQ | Trạng thái |
|---|---|---|---|---|---|
| handbook | ✅ 1 | ✅ 1 | ✅ 1 | ✅ 5 Q&A | 🟢 Hoàn thành |
| hoc_vu | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 4 Q&A | 🟢 Hoàn thành |
| dang_ky_hoc_phan | ✅ 1 | ✅ 1 | ✅ 1 | ✅ 4 Q&A | 🟢 Hoàn thành |
| hoc_phi | ✅ 4 | ✅ 4 | ✅ 5 | ✅ 4 Q&A | 🟢 Hoàn thành |
| ktx | ✅ 1 | ✅ 1 | ✅ 1 | ✅ 5 Q&A | 🟢 Hoàn thành |
| hoc_bong_ctsv | ✅ 1 | ✅ 1 | ✅ 1 | ✅ 4 Q&A | 🟢 Hoàn thành |
| diem_ren_luyen | ✅ 1 | ✅ 1 | ✅ 1 | *(trong hoc_bong)* | 🟢 Hoàn thành |
| danh_muc_nganh | ✅ 1 | ✅ 1 | ✅ 1 | ✅ 5 Q&A | 🟢 Hoàn thành |
| doan_hoi | 🔗 Web | ✅ 1 | ✅ 1 | ✅ 5 Q&A | 🟢 Hoàn thành |

**Bước tiếp theo:** Index toàn bộ `processed/` vào vector database (ChromaDB / FAISS).
