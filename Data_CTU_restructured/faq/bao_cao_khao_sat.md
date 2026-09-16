# Báo cáo phân tích khảo sát nhu cầu thông tin tân sinh viên

> Đề tài: Xây dựng trợ lý ảo hỗ trợ tân sinh viên Trường Đại học Cần Thơ
> Giai đoạn: Bước 1 — Thu thập và xây dựng kho tri thức
> Nguồn dữ liệu: `faq/KHẢO SÁT NHU CẦU THÔNG TIN CỦA TÂN SINH VIÊN (Câu trả lời).csv`
> Ngày phân tích: 2026-09-15

---

## 1. Mô tả bộ dữ liệu

- **Tổng số phản hồi thu được:** 23
- **Số phản hồi hợp lệ dùng để phân tích:** 21
- **Số phản hồi bị loại (noise):** 2

**Tiêu chí loại bỏ:** 2 phản hồi bị loại vì nội dung câu trả lời mở (mục ngành học hoặc câu hỏi mong muốn hỏi chatbot) không liên quan đến khảo sát, mang tính đùa/spam (ví dụ ghi ngành học là "LGBT", nội dung chính trị không phù hợp ngữ cảnh khảo sát sinh viên). Dữ liệu gốc được **giữ nguyên trong file CSV**, chỉ loại khi tính toán thống kê để tránh làm lệch kết quả.

### Đặc điểm mẫu (21 phản hồi hợp lệ)

| Tiêu chí | Phân bố |
|---|---|
| Thời gian nhập học | Mới nhập học (chưa hết HK1): 11 · Đã học ≥1 năm: 9 · Đã học xong HK1: 1 |
| Hệ đào tạo | Chính quy: 21/21 |
| Ngành học | Đa dạng: Khoa học máy tính, Công nghệ sinh học, Kinh tế, Y khoa, Thú y, Tự động hóa, Thương mại điện tử... (không tập trung 1 ngành) |

**Hạn chế của mẫu:** N=21 là mẫu nhỏ, không đại diện đầy đủ cho toàn bộ tân sinh viên CTU (quy mô hàng nghìn sinh viên/khóa). Kết quả dưới đây mang tính **định hướng ưu tiên**, không phải số liệu thống kê suy rộng. Nếu có thời gian, nên khảo sát thêm để đạt N ≥ 50.

---

## 2. Mức độ quan tâm theo chủ đề (thang 1–5)

Điểm trung bình mức độ quan tâm/thắc mắc của sinh viên theo từng chủ đề, xếp từ cao đến thấp:

| Hạng | Chủ đề | Điểm TB |
|---|---|---|
| 1 | Học phí, miễn giảm học phí | **4.71** |
| 1 | Học bổng | **4.71** |
| 1 | Điểm rèn luyện | **4.71** |
| 4 | Đăng ký học phần, kế hoạch học tập | 4.24 |
| 5 | Quy chế đào tạo (tín chỉ, điều kiện tốt nghiệp...) | 4.19 |
| 6 | Học trực tuyến / miễn công nhận điểm | 3.90 |
| 7 | Thủ tục hành chính (giấy tờ, xác nhận sinh viên...) | 3.86 |
| 8 | Hoạt động đoàn, hội, câu lạc bộ | 3.67 |
| 9 | Ký túc xá | 2.71 |

**Nhận xét:**
- Ba chủ đề **Học phí – Học bổng – Điểm rèn luyện** đồng hạng cao nhất, đều gắn với lợi ích tài chính/học vụ trực tiếp của sinh viên.
- **Ký túc xá** thấp bất thường (2.71) so với các chủ đề khác — có thể vì phần lớn mẫu khảo sát đã ổn định chỗ ở tại thời điểm trả lời, hoặc nhóm SV hệ chính quy CTU phần nhiều là dân địa phương/đã có chỗ ở ngoài KTX. Không nên loại bỏ chủ đề này khỏi FAQ chỉ vì điểm thấp — nhóm SV thực sự có nhu cầu KTX vẫn cần được phục vụ tốt.

---

## 3. Kênh tìm thông tin hiện tại (C2 — có thể chọn nhiều)

| Kênh | Số lượt chọn (n=21) |
|---|---|
| Website chính thức của trường/khoa | 19 |
| Hỏi bạn bè, anh chị khóa trên | 15 |
| Hỏi cố vấn học tập / giảng viên | 12 |
| Group Facebook / Zalo | 11 |
| Hỏi phòng ban liên quan trực tiếp (Đào tạo, CTSV...) | 5 |
| Khác | 1 |

**Nhận xét:** Website trường là kênh chính nhưng vẫn phụ thuộc nhiều vào hỏi người quen (bạn bè, khóa trên, CVHT) — cho thấy thông tin trên website có thể khó tra cứu hoặc không đầy đủ, sinh viên phải hỏi thêm người thật để xác nhận. Đây chính là khoảng trống mà chatbot RAG có thể lấp — trả lời trực tiếp, có nguồn, nhanh hơn hỏi người.

## 4. Đánh giá mức độ dễ/khó khi tìm thông tin hiện tại (C3)

| Đánh giá | Số lượng |
|---|---|
| Rất dễ | 4 |
| Dễ | 10 |
| Bình thường | 6 |
| Khó | 1 |

Đa số đánh giá việc tìm thông tin qua kênh hiện tại ở mức dễ/bình thường. Điều này không mâu thuẫn với sự cần thiết của chatbot: sinh viên có thể tìm được thông tin, nhưng qua nhiều bước (hỏi người, tìm nhiều nơi) — chatbot giúp **rút ngắn số bước**, không nhất thiết là giải quyết vấn đề "không tìm được".

## 5. Hình thức trả lời mong muốn (C5)

| Hình thức | Số lượng |
|---|---|
| Trả lời chi tiết kèm giải thích | 12 |
| Trả lời kèm link/nguồn tài liệu tham khảo | 6 |
| Trả lời ngắn gọn, trực tiếp | 2 |
| Không quan trọng, miễn đúng và nhanh | 1 |

**Ý nghĩa cho thiết kế Bước 3–4:** Đa số sinh viên (18/21) muốn câu trả lời **có giải thích và/hoặc có nguồn tham khảo**, không chỉ trả lời cộc lốc. Điều này củng cố quyết định thiết kế RAG có trích dẫn nguồn (`hiển thị nguồn tài liệu tham khảo` — đúng như yêu cầu ở Bước 4 của đề bài).

## 6. Khó khăn thường gặp khi mới nhập học (C1 — phân loại theo chủ đề)

| Nhóm chủ đề | Số lượt đề cập | Ví dụ |
|---|---|---|
| Đăng ký học phần / xếp KHHT | 6 | "Không biết quy trình đăng ký học phần, xếp KHHT" |
| Tìm phòng học / sơ đồ trường | 5 | "Mã phòng học đôi khi quá mới", "Trường quá rộng phải coi maps nhiều lần" |
| Điểm rèn luyện / học bổng | 4 | "Không biết ĐRL là gì, kiếm như thế nào" |
| Hòa nhập / kết bạn | 3 | "Bối rối với cách học mới, mối quan hệ mới" |
| Hồ sơ, thủ tục nhập học | 1 | "Không biết về những hồ sơ nhập học" |
| Không gặp khó khăn | 2 | "Chưa gặp", "Không có khó khăn gì" |

## 7. Chủ đề sinh viên muốn hỏi chatbot (C4 — phân loại)

| Nhóm chủ đề | Số lượt đề cập |
|---|---|
| Điểm rèn luyện (cách tính, cách kiếm điểm) | 5 |
| Học bổng (điều kiện, tổng hợp học bổng phù hợp) | 4 |
| Đăng ký học phần / xếp KHHT | 4 |
| Quy chế tốt nghiệp, môn thay thế khóa luận | 2 |
| Phòng học / sơ đồ trường | 2 |
| Hoạt động CLB, đoàn hội | 2 |
| Tài liệu/giáo trình học tập | 2 |
| Ngoài phạm vi đề tài (tâm lý, sức khỏe, kiến thức phổ thông...) | 5 |

**Nhận xét quan trọng:** Có **5/21 câu trả lời nằm ngoài phạm vi trợ lý ảo hỗ trợ tân sinh viên** — ví dụ hỏi về vũ trụ, tác hại của "chất bột", cách ăn uống lành mạnh. Đây là tín hiệu cần thiết kế cho **Bước 3 (Xử lý các câu hỏi phổ biến)**: chatbot cần có khả năng nhận diện câu hỏi ngoài phạm vi và từ chối lịch sự, tránh trả lời sai hoặc bịa (hallucination) khi không có trong kho tri thức.

---

## 8. Kết luận — liên kết sang thiết kế FAQ (đầu vào cho Bước 1 tiếp theo)

Đối chiếu độ ưu tiên khảo sát với tập FAQ hiện có (27 cặp Q&A), phát hiện lệch rõ:

| Chủ đề | Mức quan tâm (khảo sát) | Số FAQ hiện có |
|---|---|---|
| Điểm rèn luyện | 4.71 (đồng hạng 1) | **0** |
| Học bổng | 4.71 (đồng hạng 1) | 4 |
| Học phí | 4.71 (đồng hạng 1) | 3 |
| Đăng ký học phần | 4.24 | 0 (chỉ có PDF kế hoạch, chưa có FAQ) |
| Đoàn hội, CLB | 3.67 | **0** |
| Ký túc xá | 2.71 (thấp nhất) | 1 |

**Khuyến nghị bổ sung FAQ ưu tiên theo kết quả khảo sát:**
1. Điểm rèn luyện — cách tính điểm, cách cải thiện, mốc thời gian tự đánh giá (5–6 câu)
2. Đăng ký học phần / xếp kế hoạch học tập (4–5 câu)
3. Đoàn hội, CLB — cách tham gia, sinh viên 5 tốt (3–4 câu)
4. Học bổng, học phí — mở rộng thêm (3–4 câu mỗi chủ đề)
5. Thiết kế cơ chế "từ chối lịch sự" cho câu hỏi ngoài phạm vi

**Bộ câu hỏi FAQ mục tiêu:** nâng từ 27 lên 50–60 cặp Q&A, phân bổ theo đúng tỷ trọng quan tâm ở bảng trên thay vì phân bổ đều.
