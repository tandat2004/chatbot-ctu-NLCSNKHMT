# Báo cáo hoàn thiện Bước 1 — 2026-09-16

## Đã xử lý

- 14/14 file `.meta.json` hợp lệ; loại bỏ chuỗi `"null"` và giữ JSON `null` đúng kiểu.
- Sửa 6 lỗi metadata trọng tâm: 5 lỗi chuỗi `"null"` và 1 lỗi đơn vị ban hành của Quyết định 09/2022/QĐ-TTg.
- Soát số hiệu OCR và sửa các lỗi rõ ràng: `6175/QĐ-ĐHCT`, `2470/QĐ-ĐHCT`.
- 14/14 file `processed` có H1 và heading Chương/Điều/Mục theo cấu trúc Markdown.
- Dựng lại Phụ lục 1–3 của văn bản học phí 2026-2027 thành bảng Markdown có header.
- Không tự bịa hai dòng bị thiếu trong PDF gốc của Phụ lục 2: STT 76, 77 và 91 không xuất hiện trong nguồn.
- Bổ sung 5 FAQ Học phí có số liệu cụ thể từ văn bản 2026-2027.
- Cập nhật README lên phiên bản 1.1.
- **[Đợt 2 — 2026-09-16]** Bổ sung 3 file FAQ còn thiếu:
  - `faq_handbook.md` (5 câu): Sổ tay sinh viên — Phòng CTSV, CVHT, Phòng Đào tạo, liên hệ đơn vị, điểm rèn luyện.
  - `faq_danh_muc_nganh.md` (5 câu): Danh mục ngành — tổng ngành, mã ngành CNTT, viết tắt đơn vị, tra cứu, ngành Sư phạm.
  - `faq_doan_hoi.md` (5 câu): Đoàn-Hội — SV 5 tốt, tham gia CLB, mẫu biểu, đơn vị trực thuộc, văn bản quy định.
- Cập nhật README lên phiên bản 1.2: đánh dấu hoàn thành toàn bộ 8/8 chủ đề FAQ.

## Kiểm tra cuối

- 14 file raw + 14 metadata.
- 14 file processed nguồn, đều có H1.
- Phụ lục 1: 99 dòng dữ liệu.
- Phụ lục 2: 98 dòng dữ liệu xuất hiện trong nguồn (thiếu 76, 77, 91 đúng như PDF gốc).
- Phụ lục 3: 4 bảng có header đầy đủ.
- **8 file FAQ** với tổng **36 cặp câu hỏi - trả lời**: Học phí (4), Đăng ký HP (4), KTX (5), Học bổng & CTSV (4), Học vụ (4), Handbook (5), Danh mục ngành (5), Đoàn-Hội (5).

## Chưa làm

- Chưa index vector database (ChromaDB / FAISS / Pinecone).
