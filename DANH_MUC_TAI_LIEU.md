# 📚 TỔNG HỢP DANH MỤC TÀI LIỆU HỆ THỐNG CHATBOT CTU

> **Dự án:** Trợ lý ảo tư vấn quy chế, học vụ & đời sống sinh viên ĐH Cần Thơ (CTU)  
> **Cập nhật ngày:** 15/10/2026

---

## 📊 1. Thống kê tổng quan kho dữ liệu

- **Tổng số tệp tin văn bản trong kho (`data/1_raw/`):** `97` văn bản
- **Tổng số đoạn tri thức (Chunks) đã phân rã trong `chunks.jsonl`:** `694` chunks
- **Cơ sở dữ liệu Vector:** ChromaDB (`ctu_knowledge_base`) nhúng bằng mô hình chuẩn `BAAI/bge-m3`
- **Ngân hàng câu hỏi FAQ thực tế:** `474` cặp câu hỏi - đáp trích xuất thực tế (đã bổ sung nhóm Biểu mẫu & Học bổng)

---

## 🗂️ 2. Phân loại tài liệu chi tiết theo 8 nhóm chủ đề

### 1. Quy chế Đào tạo, Học vụ & Khảo thí (4 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `2025. Quy trinh chuyen sinh hoat Dang.docx` | `DOCX` | 17.4 KB | **6 chunks** | **Quy Trình** |
| 2 | `2025.QD3266_Quy_dinh_cong_tac_hoc_vu_danh_cho_sinh_vien_trinh_do_dai_hoc_hinh_thuc_chinh_quy_V3.pdf` | `PDF` | 22114.5 KB | **60 chunks** | ## B Giáo Dc Và Đào To |
| 3 | `2304_BGDDT-GDDH_08cbd.pdf` | `PDF` | 957.8 KB | **10 chunks** | ## Phụ Lục Viii |
| 4 | `Bảng phân bố thời gian tiết học.docx` | `DOCX` | 15.1 KB | **1 chunks** | **Phân Bố Tiết Học** |


### 2. Đánh giá Điểm rèn luyện & Nếp sống văn minh (2 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `2025.QD-Banhanh-QD5976-NepsongVanminhTruongDHCT0001.pdf` | `PDF` | 3462.4 KB | **21 chunks** | ## B Giáo Duc Và Đào Tao Truong Dai Hoc Can Tho |
| 2 | `28-8-2026_Quyet_dinh_ban_hanh_quy_che_danh_gia_ren_luyen_2026signedsignedsignedsignedsigned.pdf` | `PDF` | 1438.8 KB | **24 chunks** | Quy chế đánh giá kết quả rèn luyện dành cho sinh viên trình độ đại học hình thức chính quy năm ... |


### 3. Học phí, Chế độ Chính sách & Miễn giảm (3 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `1. Đơn xin hưởng Nghị định 116 -2025_-_2026.docx` | `DOCX` | 7.8 KB | **3 chunks** | **Đơn Đề Nghị Hưởng  Và Cam Kết Bồi Hoàn Học Phí, Chi Phí Sinh Hoạt** |
| 2 | `2. Đơn xin KHONG hưởng Nghị định 116 -2025_-_2026.docx` | `DOCX` | 6.7 KB | **2 chunks** | **Đơn Đề Nghị** |
| 3 | `MucHocPhi_2627.pdf` | `PDF` | 695.4 KB | **30 chunks** | Phụ lục về việc mức học phí áp dụng cho năm học 2026-2027 2276 |


### 4. Các chương trình Học bổng (K52, Doanh nghiệp, Khuyến học) (6 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `10-8-2026_thong_bao_trien_khai_hoc_bong_VietHope_2026signed.pdf` | `PDF` | 476.3 KB | *(File phụ trợ / Biểu mẫu)* | 10-8-2026 thong bao trien khai hoc bong VietHope 2026signed |
| 2 | `11-8-2026_thong_bao_trien_khai_hoc_bong_Hop_tac_va_Se_chia_2026signed.pdf` | `PDF` | 478.5 KB | **5 chunks** | Thông báo về việc xét chọn học bổng Tân sinh viên Đại học Cần Thơ |
| 3 | `13-8-2026_thong_bao_trien_khai_cap_hoc_bong_HKH_An_Giang_2026signed.pdf` | `PDF` | 495.5 KB | **7 chunks** | ## Phòng Công Tác Sinh Viên |
| 4 | `13-8-2026_thong_bao_trien_khai_cap_hoc_bong_HKH_Dong_Thap_2026signed.pdf` | `PDF` | 499.7 KB | **8 chunks** | Thông báo về việc tiếp nhận hồ sơ dự tuyển các chương trình học bổng, năm học 2026 - 2027; Phòn... |
| 5 | `17-8-2026_Thong_bao_trien_khai_hoc_bong_WEAV_2026signed.pdf` | `PDF` | 496.3 KB | **6 chunks** | Thông báo về việc xét chọn học bổng Nữ sinh viên Khóa 52 |
| 6 | `22-08-2026-Thong_bao_trien_khai_hoc_bong_Orion_2026signed.pdf` | `PDF` | 471.1 KB | **4 chunks** | ## Phòng Công Tác Sinh Viên |


### 5. Ký túc xá & Đời sống sinh viên (6 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `BM_40.Phiếu đăng ký chỗ ở Nội trú Dành cho Sinh viên khóa mới.pdf` | `PDF` | 214.3 KB | **2 chunks** | ## Phòng Công Tác Sinh Viên Trung Tâm Phục Vụ Sinh Viên |
| 2 | `BM_41.Phiếu đăng ký chỗ ở Nội trú Dành cho Sinh viên hoac Học viên không đăng ký online được.pdf` | `PDF` | 187.3 KB | **3 chunks** | ## Đơn Xin Ở Ký Túc Xá |
| 3 | `BM_42.Đơn xin thôi ở KTX trước thời hạn.pdf` | `PDF` | 191.5 KB | **5 chunks** | ## Trƣờng Đại Học Cần Thơ Phòng Công Tác Sinh Viên |
| 4 | `BM_44.Đơn xin hoàn phí KTX chênh lệch.pdf` | `PDF` | 232.4 KB | **2 chunks** | ## Trƣờng Đại Học Cần Thơ Phòng Công Tác Sinh Viên |
| 5 | `BM_45.Phiếu đề nghị sửa chữa, thay thiết bị KTX.pdf` | `PDF` | 185.9 KB | **1 chunks** | ## Phiếu Đề Nghị Sửa Chữa |
| 6 | `Ky tuc xa sinh vien.docx` | `DOCX` | 5417.0 KB | **4 chunks** | ### Ký Túc Xá Đại Học Cần Thơ - An Tâm Nơi Ở, Sẵn Sàng Cho Hành Trình K52 |


### 6. Tuyển sinh, Nhập học & Tân sinh viên (K52) (7 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `30-7-2026_Thng_bo_hc_bng_Tn_sinh_vin_K52_nm_2026_HCTD_Can_Thosigned.pdf` | `PDF` | 481.9 KB | **5 chunks** | Thông báo về việc dự tuyển học bổng "Tân sinh viên đặc biệt khó khăn" năm 2026 |
| 2 | `Hoc bong khuyen hoc K52.pdf` | `PDF` | 494.3 KB | **5 chunks** | Thông báo về việc xét cấp học bổng "Khuyến học Đại học Cần Thơ" - Tân sinh viên khóa 52 |
| 3 | `Huong_Dan_Xem_TKB_K52.pdf` | `PDF` | 238.7 KB | **2 chunks** | ## Cách Xem Thời Khóa Biểu Học Tập |
| 4 | `Kết quả TT UTXT 2026_Web.pdf` | `PDF` | 154.2 KB | **48 chunks** | ## Danh Sách Thí Sinh Đăng Ký Tuyển Thẳng, Ưu Tiên Xét Tuyển Vào Đại Học Chính Quy Năm 2026 |
| 5 | `LICH_GDQP_K52_HK1_2026_2027.signed.signed.signed.pdf` | `PDF` | 572.3 KB | **6 chunks** | ## Lịch Học Giáo Dục Quốc Phòng Và An Ninh Khóa 52 Học Kỳ I, Năm Học 2026-2027 |
| 6 | `TB_Bảng Quy doi diem thi V-SAT 2026.docx` | `DOCX` | 45.2 KB | **12 chunks** | **Thông Báo** |
| 7 | `Thoi khoa Bieu K52_Daitra.xlsx` | `XLSX` | 14.1 KB | *(File phụ trợ / Biểu mẫu)* | Thoi khoa Bieu K52 Daitra |


### 7. Danh mục Biểu mẫu Đơn từ Hành chính (BM_1 – BM_45) (42 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `BM_1.Đơn đề nghị xét miễn và công nhận điểm miễn (có chứng chỉ Ngoại ngữ, Tin học, GDTC, GDQP).docx` | `DOCX` | 11.4 KB | **4 chunks** | #### Đơn Đề Nghị Xét Miễn Và Công Nhận Điểm M |
| 2 | `BM_10.Đơn đề nghị xác nhận hoàn thành học phần Giáo dục thể chất.docx` | `DOCX` | 7.5 KB | **1 chunks** | **Đơn Đề Nghị Xác Nhận Hoàn Thành** |
| 3 | `BM_11.Đơn đề nghị xác nhận Quy đổi điểm học tập từ thang điểm 4 sang thang điểm 10.docx` | `DOCX` | 6.8 KB | **1 chunks** | **Đơn Đề Nghị Quy Đổi Điểm Học Tập** |
| 4 | `BM_12.Đơn đề nghị cấp bản sao bằng tốt nghiệp.docx` | `DOCX` | 6.1 KB | **2 chunks** | **Đơn Đề Nghị Cấp Bản Sao Bằng Tốt Nghiệp** |
| 5 | `BM_13.Mẫu giấy ủy quyền nhận thay văn bằng tốt nghiệp.docx` | `DOCX` | 8.3 KB | **3 chunks** | **Giấy Ủy Quyền** |
| 6 | `BM_14.Mẫu giấy ủy quyền nhận thay bản sao văn bằng tốt nghiệp.docx` | `DOCX` | 8.3 KB | **3 chunks** | **Giấy Ủy Quyền** |
| 7 | `BM_15.Mẫu đơn đề nghị chỉnh sửa nội dung văn bằng tốt nghiệp.docx` | `DOCX` | 6.0 KB | **4 chunks** | **Đơn Đề Nghị** |
| 8 | `BM_16.Mẫu đơn đề nghị cấp lại văn bằng tốt nghiệp (đối với trường hợp Trường ĐHCT viết hoặc in sai).docx` | `DOCX` | 5.9 KB | **4 chunks** | **Đơn Đề Nghị** |
| 9 | `BM_17.Mẫu phiếu thanh toán ra trường.docx` | `DOCX` | 6.3 KB | **2 chunks** | BM 17.Mẫu phiếu thanh toán ra trường |
| 10 | `BM_18.Đơn đề nghị xét miễn và công nhận điểm miễn.docx` | `DOCX` | 11.7 KB | **4 chunks** | #### Đơn Đề Nghị Xét Miễn Và Công Nhận Điểm M |
| 11 | `BM_19.Mẫu đơn Phụ lục I Hỗ trợ chi phí học tập theo QĐ 66-2013 QĐ-TTg của Thủ tướng chính phủ.docx` | `DOCX` | 6.7 KB | **2 chunks** | **Đơn Đề Nghị Hỗ Trợ Chi Phí Học Tập** |
| 12 | `BM_2.Đơn đề nghị xét miễn và công nhận điểm HP  (bảo lưu điểm đã học ĐH trước đây).docx` | `DOCX` | 10.6 KB | **4 chunks** | #### Đơn Đề Nghị Xét Miễn Và Công Nhận Điểm Học Phần |
| 13 | `BM_20.Mẫu đơn xác nhận hộ nghèo.docx` | `DOCX` | 8.4 KB | **3 chunks** | Ubnd Huyện --------(1)--------- **Cộng Hoà Xã Hội Chủ Nghĩa Việt Nam** |
| 14 | `BM_21.Mẫu đơn xác nhận hộ cận nghèo.docx` | `DOCX` | 7.9 KB | **2 chunks** | Ubnd Huyện ---------------- **Cộng Hoà Xã Hội Chủ Nghĩa Việt Nam** |
| 15 | `BM_22.Đơn xin trợ cấp khó khăn đột xuất.docx` | `DOCX` | 7.1 KB | **3 chunks** | **Đơn Xin Xét Trợ Cấp Khó Khăn Đột Xuất** |
| 16 | `BM_23.Đơn xin trợ cấp xã hội.docx` | `DOCX` | 8.1 KB | **2 chunks** | ## Đơn Xin Xét Trợ Cấp Xã Hội |
| 17 | `BM_24.Mẫu 01 Ban hành theo Thông tư số 26.2012TT-BLĐTBXH.docx` | `DOCX` | 6.9 KB | **7 chunks** | **Mẫu Số 01** |
| 18 | `BM_25.Giấy cam kết trả nợ.docx` | `DOCX` | 7.1 KB | **3 chunks** | **Mẫu Số: 05/Tdsv** |
| 19 | `BM_26.Giấy xác nhận vay vốn mẫu 01.TDSV.docx` | `DOCX` | 7.4 KB | **2 chunks** | **Mẫu Số: 01/Tdsv** |
| 20 | `BM_27.Đơn xin học lại mẫu 1a (áp dụng cho sinh viên tạm nghỉ vì lý do khác).docx` | `DOCX` | 7.9 KB | **3 chunks** | **Đơn Xin Học Lại** |
| 21 | `BM_28.Đơn xin học lại mẫu 1b (áp dụng cho sinh viên tạm nghỉ với lý do trị bệnh).docx` | `DOCX` | 7.9 KB | **3 chunks** | **Đơn Xin Học Lại** |
| 22 | `BM_29.Đơn xin học lại mẫu 1c (áp dụng cho sinh viên học lại vì bị đình chỉ học tập có thời hạn).docx` | `DOCX` | 7.9 KB | **3 chunks** | **Đơn Xin Học Lại** |
| 23 | `BM_3.Đơn đề nghị xét miễn và công nhận điểm HP (Trường ĐHCT cử đi học tập).docx` | `DOCX` | 7.0 KB | **4 chunks** | Đơn về việc cho phép sinh viên đi học tập của Hiệu trưởng Trường Đại học Cần Thơ. |
| 24 | `BM_30.Đơn xin tạm nghỉ học vì bận việc riêng hay lý do khác.docx` | `DOCX` | 7.9 KB | **3 chunks** | **Đơn Xin Tạm Nghỉ Học** |
| 25 | `BM_31.Đơn xin tạm nghỉ với lý do điều trị bệnh.docx` | `DOCX` | 7.9 KB | **2 chunks** | **Đơn Xin Tạm Nghỉ Học** |
| 26 | `BM_32.Đơn xin tạm hoãn nghĩa vụ quân sự.docx` | `DOCX` | 7.7 KB | **2 chunks** | **Đơn Xin Xác Nhận** |
| 27 | `BM_33.Đơn xác nhận sinh viên Trường.docx` | `DOCX` | 7.7 KB | **2 chunks** | **Đơn Xin Xác Nhận** |
| 28 | `BM_34.Giấy xác nhận sinh viên (Tiếng Anh).docx` | `DOCX` | 5.4 KB | **1 chunks** | **Letter Of Verification** |
| 29 | `BM_35.Mẫu đơn miễn giảm học phí theo Nghị định 81.2021.NĐ-CP.pdf` | `PDF` | 495.2 KB | **1 chunks** | Don Dè Ngh! Min, Giàm Hqc Phí |
| 30 | `BM_36.Mẫu đơn đăng ký vay vốn theo lớp.xlsx` | `XLSX` | 9.0 KB | *(File phụ trợ / Biểu mẫu)* | BM 36.Mẫu đơn đăng ký vay vốn theo lớp |
| 31 | `BM_37.Đơn xin chuyển trường.docx` | `DOCX` | 8.5 KB | **7 chunks** | BM 37.Đơn xin chuyển trường |
| 32 | `BM_38.Mẫu đơn xin thôi học (lý do khác).docx` | `DOCX` | 5.7 KB | **2 chunks** | **Đơn Xin Thôi Học** |
| 33 | `BM_39.Đơn xin chuyển chương trình, ngành đào tạo (theo Quy trình hướng dẫn 1982.HD-ĐHCT).docx` | `DOCX` | 8.4 KB | **3 chunks** | **Đơn Đề Nghị Chuyển Chương Trình, Ngành Đào Tạo** |
| 34 | `BM_4.Đơn đề nghị điểm I (vắng thi kết thúc học phần).docx` | `DOCX` | 8.3 KB | **2 chunks** | **Ðơn Xin Phép Vắng Thi Kết Thúc Học Phần** |
| 35 | `BM_43.Đơn xin hoàn phí Ký túc xá.pdf` | `PDF` | 236.7 KB | **3 chunks** | ## Đơn Xin Hoàn Phí Ktx |
| 36 | `BM_5.Đơn đề nghị thay đổi thời khóa biểu lớp học phần.docx` | `DOCX` | 7.6 KB | **2 chunks** | **Đơn Đề Nghị Thay Đổi Thời Khóa Biểu Lớp Học Phần** |
| 37 | `BM_6.Đơn đề nghị mở lớp học phần.docx` | `DOCX` | 7.1 KB | **2 chunks** | **Đơn Đề Nghị Mở Lớp Học Phần** |
| 38 | `BM_7.Đơn đề nghị phục hồi lớp học phần bị xóa.docx` | `DOCX` | 6.8 KB | **1 chunks** | **Đơn Đề Nghị Phục Hồi Lớp Học Phần** |
| 39 | `BM_8.Đơn đề nghị xác nhận trình độ ngoại ngữ A - Anh văn hoặc A - Pháp văn (các ngành đại trà từ khóa 44 về trước).docx` | `DOCX` | 5.9 KB | **1 chunks** | **Đơn Đề Nghị Xác Nhận Trình Độ Ngoại Ngữ** |
| 40 | `BM_9.Đơn đề nghị xác nhận trình độ ngoại ngữ bậc 3.6 B1 - Anh văn hoặc B1 - Pháp văn-các ngành đại trà từ khóa 45.docx` | `DOCX` | 6.0 KB | **1 chunks** | **Đơn Đề Nghị Xác Nhận Trình Độ Ngoại Ngữ** |
| 41 | `phieudangkychuyenganh.docx` | `DOCX` | 8.6 KB | **2 chunks** | **Phiếu Đăng Ký Chuyên Ngành Khóa 52** |
| 42 | `phieuThongtinsv2026.docx` | `DOCX` | 10.2 KB | **12 chunks** | **Phiếu Thông Tin Sinh Viên Khóa 52** |


### 8. Cơ sở vật chất, Cẩm nang & Kỹ năng sinh viên (27 tài liệu)

| STT | Tên tệp tin | Định dạng | Dung lượng | Số chunks | Tiêu đề văn bản / Trích dẫn nhận diện |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `17-8-2026_Thng_bo_hc_bng_Tip_sc_n_trng_-_Bo_Tui_tr_nm_2026signed.pdf` | `PDF` | 479.7 KB | **3 chunks** | Thông báo về việc dự tuyển học bổng "Tiếp sức đến trường 2026" của Báo Tuổi trẻ |
| 2 | `2025-11_CV-DHCT_Thong bao_Danh muc To hop xet tuyen dai hoc chinh quy nam 2025_V2.docx` | `DOCX` | 44.5 KB | **15 chunks** | **Thông Báo** |
| 3 | `2025.Quyet_dinh_3512-_Ban_hanh_Quy_dinh_ve_quan_ly-_khai_thac_mang_thong_tin-Truong_DHCT.pdf` | `PDF` | 5052.1 KB | **36 chunks** | ## Bô Giáo Duc Và Đào To Truòng Đai Hqc Càn Tho |
| 4 | `2026-07-10-TB2217-DHCT_Thong bao xet tuyen CTCLC va CTTT_PT5_2026.docx` | `DOCX` | 14.0 KB | **11 chunks** | **Thông Báo** |
| 5 | `2026-07-10-TB2217-DHCT_Thong-bao-xet-tuyen-CTCLC-va-CTTT_PT5_2026.signed.signed.signed.pdf` | `PDF` | 481.4 KB | *(File phụ trợ / Biểu mẫu)* | 2026-07-10-TB2217-DHCT Thong-bao-xet-tuyen-CTCLC-va-CTTT PT5 2026.signed.signed.signed |
| 6 | `20260731-TB2429-DHCT_Thong bao Bang quy doi diem Hoc ba nam 2026.docx` | `DOCX` | 61.7 KB | **23 chunks** | **Thông Báo** |
| 7 | `2883_Phu luc va Đơn_Huong_dan_xet_mien_rut_hoc_phan_K51.docx` | `DOCX` | 13.9 KB | **8 chunks** | #### Đơn Đề Nghị Xét Miễn Và Công Nhận Điểm M |
| 8 | `2884_Phu luc va Đơn_mien_HP_va_HP_SV_CTTTCLC_K51_do_co_Chung_chi_TA_bac_3_tro_len.docx` | `DOCX` | 11.6 KB | **5 chunks** | **.Bảng Quy Đổi Chuẩn Trình Độ Ngoại Ngữ Tiếng Anh** |
| 9 | `30-7-2026 KH_SHNAM_26.signed.signed.signed.signed.pdf` | `PDF` | 1053.0 KB | **20 chunks** | ## Đại Học Cần Thơ |
| 10 | `30-7-2026_KH_SHNAM_26signedsignedsignedsigned.pdf` | `PDF` | 1053.0 KB | *(File phụ trợ / Biểu mẫu)* | 30-7-2026 KH SHNAM 26signedsignedsignedsigned |
| 11 | `Cac khu thuoc Dai hoc Can Tho.docx` | `DOCX` | 22714.6 KB | **32 chunks** | Cac khu thuoc Dai hoc Can Tho |
| 12 | `Cach xem thoi khoa bieu.docx` | `DOCX` | 297.4 KB | *(File phụ trợ / Biểu mẫu)* | Cach xem thoi khoa bieu |
| 13 | `CTU PowerPoint Template.pptx` | `PPTX` | 763.8 KB | *(File phụ trợ / Biểu mẫu)* | CTU PowerPoint Template |
| 14 | `CV_2457_BGDT_huong dan nop minh chung uu tien xet tuyen.pdf` | `PDF` | 1352.6 KB | **13 chunks** | ## Phụ Lục Ix |
| 15 | `Ho so nhap hoc gom co nhung gi.docx` | `DOCX` | 1354.9 KB | **1 chunks** | Hồ Sơ Nhập Học Gồm: |
| 16 | `Kiosk hỗ trợ cấp giấy tờ hành chính tự động cho tâm sinh viên.txt` | `TXT` | 1.5 KB | *(File phụ trợ / Biểu mẫu)* | Kiosk hỗ trợ cấp giấy tờ hành chính tự động cho tâm sinh viên |
| 17 | `KynangNhandienPhongchongLuadaoTructuyen.pdf` | `PDF` | 24442.4 KB | **49 chunks** | ## Lời Mở Đầu |
| 18 | `So do huong dan lam thu tuc nhap hoc.docx` | `DOCX` | 1879.1 KB | **5 chunks** | Hướng Dẫn Tân Sinh Viên K52 Làm Thủ Tục Nhập Học |
| 19 | `So tay huong dan thuong hieu.docx` | `DOCX` | 11505.1 KB | **8 chunks** | Hướng Dẫn Thương Hiệu |
| 20 | `So_tay_huong_dan_thuong_hieu_Dai_hoc_Can_Tho.pdf` | `PDF` | 4365.3 KB | **16 chunks** | So tay huong dan thuong hieu Dai hoc Can Tho |
| 21 | `Sơ đồ phòng học.docx` | `DOCX` | 1958.8 KB | **5 chunks** | Ký Hiệu Phòng Học Của Từng Dãy Nhà Học |
| 22 | `TB2049_KQTT-ƯTXT_2026_Web.docx` | `DOCX` | 24.6 KB | **7 chunks** | Thông báo về việc xét hồ sơ đăng ký tuyển thẳng, ưu tiên xét tuyển và phân bổ học sinh hoàn thà... |
| 23 | `TB2532_Thong bao ket qua va diem chuan_2026_web.docx` | `DOCX` | 49.3 KB | **15 chunks** | **Thông Báo** |
| 24 | `Thong bao tren Website tan sinh vien Khoa 52.docx` | `DOCX` | 2516.7 KB | **7 chunks** | Thông báo về việc tiếp nhận sinh hoạt Đoàn dành cho Tân Sinh viên Khóa 52** |
| 25 | `Thong tin lien he mot so don vi.docx` | `DOCX` | 5.7 KB | **2 chunks** | Thong tin lien he mot so don vi |
| 26 | `Thu vien.docx` | `DOCX` | 4111.8 KB | **11 chunks** | Thu vien |
| 27 | `Đăng nhập hệ thống tích hợp.docx` | `DOCX` | 693.9 KB | **2 chunks** | Đăng nhập hệ thống tích hợp |


---

## 🚀 3. Hướng dẫn nạp thêm hoặc cập nhật tài liệu mới

Hệ thống đã được tích hợp công cụ tự động hóa toàn diện qua script [ingest_file.py](./ingest_file.py).

Khi trường ban hành văn bản quy định mới (PDF/DOCX), bạn chỉ cần chạy đúng **1 dòng lệnh duy nhất**:

```bash
# Từ thư mục gốc dự án:
python ingest_file.py "data_pipeline/data/1_raw/ten_file_moi.pdf"
```

### Cơ chế tự động bên dưới:

1. **Trích xuất thông minh:** Tự động dùng `Docling` đọc hiểu văn bản, trích xuất cấu trúc bảng biểu, tiêu đề, điều khoản.

2. **Cắt đoạn chuẩn (Chunking):** Tự động chia đoạn có ngữ cảnh tiêu đề và lưu nối tiếp vào `chunks.jsonl` (tự động khử trùng lặp).

3. **Vector hóa siêu tốc:** Tự động gọi mô hình `BAAI/bge-m3` nhúng và `upsert` vào ChromaDB chỉ trong **15 – 25 giây** mà không làm ảnh hưởng các tài liệu đã có.
