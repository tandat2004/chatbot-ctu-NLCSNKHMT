# -*- coding: utf-8 -*-
"""
Script crawl dữ liệu Q&A từ K52 Buddy Chatbot (aibot.vnptiengiang.vn)
được nhúng trên trang tansinhvien.ctu.edu.vn.

CÁCH DÙNG:
1. Mở chatbot trên trình duyệt, mở DevTools > Network > Wasm/WS,
   tìm request "ws_stream?token=..." đang mở (status 101).
2. Copy toàn bộ URL (kèm token) vào biến WS_URL bên dưới.
   LƯU Ý: token JWT thường có hạn dùng ngắn -> nếu script báo lỗi
   kết nối/401, mở lại trang, lấy token mới rồi chạy lại.
3. Sửa danh sách QUESTIONS theo nhu cầu (sổ tay SV, điểm rèn luyện, đoàn hội...).
4. Chạy: python crawl_ctu_chatbot.py
   Kết quả lưu vào ctu_chatbot_qa.csv (question, answer, source_files)

LƯU Ý ĐẠO ĐỨC/PHÁP LÝ:
- Chỉ dùng để thu thập dữ liệu tham khảo phục vụ mục đích học thuật (niên luận).
- Gửi câu hỏi với tốc độ vừa phải (đã có time.sleep), tránh làm quá tải server.
- Không public token trong code khi đưa lên GitHub (dùng biến môi trường).
"""

import json
import time
import csv
import os
import websocket  # pip install websocket-client

# ====== CẤU HÌNH ======
# Dán URL đầy đủ (kèm ?token=...) copy từ DevTools > Network > ws_stream
WS_URL = os.environ.get(
    "CTU_WS_URL",
    "wss://aibot.vnpttiengiang.vn/ws/chat/ws_stream?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMGNkZDFkNTktMTI1Yi00OTNlLTk3NDctYjJjMDlhYWY3ZmQ4IiwicGVybWlzc2lvbnMiOlsiRklMRV9NQU5BR0VSIiwiQk9UX1RFTVBMQVRFX01BTkFHRVIiLCJCT1RfTUFOQUdFUiJdLCJ0eXBlIjoiaW50ZWdyYXRpb24ifQ.Qr3PrU-QHHRZJKey_-t3wBltxiOoVsvIDyuvGGhmNws&bot_id=245e62c9-72de-4f98-a099-e4a5f60204d5"
)
# Danh sách câu hỏi cần crawl - tự bổ sung thêm theo chủ đề
QUESTIONS = [

    # =========================================================
    # --- NHẬP HỌC / TÂN SINH VIÊN ---
    # =========================================================

    "Tân sinh viên cần làm những thủ tục gì sau khi trúng tuyển?",
    "Quy trình nhập học của tân sinh viên Đại học Cần Thơ như thế nào?",
    "Hồ sơ nhập học của tân sinh viên gồm những giấy tờ gì?",
    "Tân sinh viên cần nộp bản chính hay bản sao các giấy tờ khi nhập học?",
    "Những giấy tờ nào trong hồ sơ nhập học phải có công chứng?",
    "Nếu thiếu một giấy tờ trong hồ sơ nhập học thì phải làm thế nào?",
    "Tân sinh viên có thể bổ sung hồ sơ sau khi nhập học không?",
    "Thời hạn hoàn thành hồ sơ nhập học là khi nào?",
    "Tân sinh viên nhập học ở đâu?",
    "Tân sinh viên có thể nhập học trực tuyến không?",
    "Quy trình nhập học trực tuyến gồm những bước nào?",
    "Tân sinh viên cần đăng ký thông tin cá nhân ở đâu?",
    "Tân sinh viên cần khai báo lý lịch sinh viên như thế nào?",
    "Tân sinh viên cần nộp giấy khám sức khỏe không?",
    "Sinh viên thuộc diện miễn hoặc giảm giấy tờ nào khi nhập học không?",
    "Sinh viên là người dân tộc thiểu số cần bổ sung giấy tờ gì?",
    "Sinh viên thuộc diện chính sách cần nộp thêm giấy tờ gì khi nhập học?",
    "Tân sinh viên cần đăng ký bảo hiểm y tế khi nhập học như thế nào?",
    "Tân sinh viên cần đóng những khoản tiền nào khi nhập học?",
    "Sau khi nhập học tân sinh viên cần làm những việc gì tiếp theo?",
    "Tân sinh viên nhận thẻ sinh viên như thế nào?",
    "Tân sinh viên nhận tài khoản sinh viên ở đâu?",
    "Tân sinh viên làm thế nào để biết mã số sinh viên của mình?",
    "Sinh viên bị sai thông tin cá nhân sau khi nhập học phải làm thế nào?",
    "Thông tin trên giấy báo trúng tuyển bị sai thì phải xử lý như thế nào?",
    "Sinh viên không thể đến nhập học đúng thời gian quy định thì phải làm gì?",
    "Có thể ủy quyền cho người khác làm thủ tục nhập học không?",
    "Trường hợp trúng tuyển nhưng không nhập học đúng hạn thì sao?",
    "Sinh viên muốn xác nhận nhập học cần thực hiện ở đâu?",
    "Có cần mang căn cước công dân khi làm thủ tục nhập học không?",


    # =========================================================
    # --- HỌC PHÍ / CÁC KHOẢN PHẢI ĐÓNG ---
    # =========================================================

    "Học phí năm học 2026-2027 của Đại học Cần Thơ là bao nhiêu?",
    "Mức học phí năm học 2026-2027 được quy định như thế nào?",
    "Học phí được tính theo tín chỉ hay theo học kỳ?",
    "Mức học phí của mỗi tín chỉ là bao nhiêu?",
    "Các ngành khác nhau có mức học phí khác nhau không?",
    "Học phí của ngành Công nghệ thông tin là bao nhiêu?",
    "Học phí chương trình đào tạo chất lượng cao được tính như thế nào?",
    "Học phí các học phần giáo dục thể chất được tính như thế nào?",
    "Học phí các học phần giáo dục quốc phòng được tính như thế nào?",
    "Sinh viên học lại một học phần phải đóng học phí như thế nào?",
    "Sinh viên học cải thiện có phải đóng học phí không?",
    "Sinh viên học vượt có phải đóng thêm học phí không?",
    "Sinh viên đăng ký ít tín chỉ có mức học phí như thế nào?",
    "Sinh viên đăng ký nhiều tín chỉ có phải đóng học phí tương ứng không?",
    "Sinh viên rút học phần có được hoàn lại học phí không?",
    "Điều kiện để được hoàn học phí khi rút học phần là gì?",
    "Thời hạn rút học phần để được hoàn học phí là khi nào?",
    "Sinh viên bảo lưu có phải đóng học phí không?",
    "Sinh viên thôi học có được hoàn học phí không?",
    "Sinh viên nợ học phí có được đăng ký học phần không?",
    "Sinh viên chưa đóng học phí có được dự thi không?",
    "Hạn đóng học phí mỗi học kỳ là khi nào?",
    "Có thể đóng học phí trực tuyến không?",
    "Các phương thức thanh toán học phí gồm những gì?",
    "Có thể đóng học phí qua ngân hàng không?",
    "Có thể đóng học phí qua ứng dụng ngân hàng không?",
    "Nếu chuyển khoản nhưng hệ thống chưa ghi nhận học phí thì phải làm gì?",
    "Làm thế nào để kiểm tra mình còn nợ học phí?",
    "Sinh viên có thể xem lịch sử đóng học phí ở đâu?",
    "Có thể xin gia hạn đóng học phí không?",
    "Điều kiện để được gia hạn đóng học phí là gì?",
    "Sinh viên thuộc diện khó khăn có được hỗ trợ học phí không?",
    "Những khoản thu nào ngoài học phí mà sinh viên phải đóng?",
    "Học phí có thay đổi theo từng năm học không?",
    "Văn bản nào quy định mức học phí năm học 2026-2027?",
    "Mức học phí được ban hành bởi cơ quan nào?",
    "Quy định học phí áp dụng cho những khóa sinh viên nào?",


    # =========================================================
    # --- ĐĂNG KÝ HỌC PHẦN / CÔNG TÁC HỌC VỤ ---
    # =========================================================

    "Sinh viên đăng ký học phần như thế nào?",
    "Đăng ký học phần được thực hiện ở đâu?",
    "Thời gian đăng ký học phần được quy định như thế nào?",
    "Sinh viên được đăng ký bao nhiêu tín chỉ trong một học kỳ?",
    "Số tín chỉ tối đa sinh viên được đăng ký là bao nhiêu?",
    "Số tín chỉ tối thiểu sinh viên phải đăng ký là bao nhiêu?",
    "Khi nào sinh viên được đăng ký học phần bổ sung?",
    "Sinh viên có được thay đổi học phần đã đăng ký không?",
    "Sinh viên có được rút học phần sau khi đăng ký không?",
    "Điều kiện để hủy học phần là gì?",
    "Điều kiện để đăng ký một học phần là gì?",
    "Học phần tiên quyết là gì?",
    "Học phần học trước là gì?",
    "Học phần song hành là gì?",
    "Nếu chưa đạt học phần tiên quyết thì có được đăng ký học phần không?",
    "Sinh viên không đăng ký được học phần vì hết chỗ phải làm thế nào?",
    "Nếu lớp học phần bị đầy thì sinh viên phải xử lý thế nào?",
    "Sinh viên có thể xin mở thêm lớp học phần không?",
    "Sinh viên có thể đăng ký học phần của lớp khác không?",
    "Sinh viên có được học vượt chương trình không?",
    "Sinh viên có được đăng ký học phần ngoài chương trình đào tạo không?",
    "Sinh viên có được đăng ký học phần ở học kỳ hè không?",
    "Học kỳ hè được tổ chức như thế nào?",
    "Quy định về học lại như thế nào?",
    "Quy định về học cải thiện như thế nào?",
    "Sinh viên được học lại một học phần bao nhiêu lần?",
    "Điểm học lại được tính vào điểm trung bình như thế nào?",
    "Sinh viên bị điểm F phải làm gì?",
    "Điểm F có ảnh hưởng đến học bổng không?",
    "Điểm F có ảnh hưởng đến xếp loại tốt nghiệp không?",
    "Quy định về nghỉ học như thế nào?",
    "Sinh viên nghỉ học tạm thời có những hình thức nào?",
    "Quy định về bảo lưu kết quả học tập như thế nào?",
    "Điều kiện để được bảo lưu kết quả học tập là gì?",
    "Sinh viên được bảo lưu trong thời gian bao lâu?",
    "Thủ tục xin bảo lưu kết quả học tập gồm những gì?",
    "Sinh viên muốn quay lại học sau thời gian bảo lưu phải làm gì?",
    "Sinh viên xin thôi học cần làm thủ tục gì?",
    "Sinh viên có thể chuyển ngành học không?",
    "Điều kiện chuyển ngành học là gì?",
    "Sinh viên có thể chuyển chương trình đào tạo không?",
    "Sinh viên có thể chuyển trường không?",
    "Điều kiện để được chuyển trường là gì?",
    "Sinh viên muốn học cùng lúc hai ngành phải làm thế nào?",
    "Điều kiện học cùng lúc hai ngành là gì?",
    "Sinh viên có thể học ngành thứ hai từ năm mấy?",
    "Quy định về học phần thay thế như thế nào?",
    "Quy định về công nhận học phần tương đương như thế nào?",


    # =========================================================
    # --- ĐIỂM / ĐÁNH GIÁ KẾT QUẢ HỌC TẬP ---
    # =========================================================

    "Cách tính điểm học phần như thế nào?",
    "Điểm quá trình được tính như thế nào?",
    "Điểm thi cuối kỳ được tính như thế nào?",
    "Điểm học phần được quy đổi sang điểm chữ như thế nào?",
    "Điểm chữ A, B, C, D, F tương ứng với mức điểm nào?",
    "Điểm trung bình học kỳ được tính như thế nào?",
    "Điểm trung bình tích lũy được tính như thế nào?",
    "Tín chỉ dùng để tính điểm trung bình là gì?",
    "Học phần không đạt có được tính vào điểm trung bình không?",
    "Điểm học lại có thay thế điểm cũ không?",
    "Điểm học cải thiện được tính như thế nào?",
    "Sinh viên có được phúc khảo điểm không?",
    "Thủ tục phúc khảo điểm như thế nào?",
    "Thời hạn đăng ký phúc khảo là khi nào?",
    "Sinh viên kiểm tra điểm ở đâu?",
    "Nếu điểm trên hệ thống bị sai thì phải làm thế nào?",
    "Điểm danh có ảnh hưởng đến kết quả học phần không?",
    "Sinh viên nghỉ học quá số buổi quy định thì sao?",
    "Điều kiện được dự thi cuối kỳ là gì?",
    "Trường hợp không đủ điều kiện dự thi thì phải làm gì?",
    "Sinh viên vắng thi có được thi bù không?",
    "Quy định về thi lại như thế nào?",
    "Sinh viên được thi lại trong trường hợp nào?",


    # =========================================================
    # --- XẾP LOẠI HỌC TẬP / CẢNH BÁO HỌC VỤ ---
    # =========================================================

    "Sinh viên được xếp loại học tập như thế nào?",
    "Các mức xếp loại học tập gồm những loại nào?",
    "Điều kiện để đạt loại xuất sắc là gì?",
    "Điều kiện để đạt loại giỏi là gì?",
    "Điều kiện để đạt loại khá là gì?",
    "Điều kiện để đạt loại trung bình là gì?",
    "Khi nào sinh viên bị cảnh báo học vụ?",
    "Điểm trung bình bao nhiêu thì bị cảnh báo học vụ?",
    "Sinh viên bị cảnh báo học vụ phải làm gì?",
    "Sinh viên bị cảnh báo học vụ bao nhiêu lần thì bị buộc thôi học?",
    "Sinh viên có thể xin xem xét khi bị cảnh báo học vụ không?",
    "Những trường hợp nào sinh viên bị buộc thôi học?",
    "Sinh viên có thể khiếu nại quyết định buộc thôi học không?",
    "Thời gian tối đa để hoàn thành chương trình đào tạo là bao lâu?",
    "Sinh viên vượt quá thời gian đào tạo tối đa thì sao?",
    "Thời gian đào tạo chuẩn của chương trình đại học là bao lâu?",


    # =========================================================
    # --- CHƯƠNG TRÌNH ĐÀO TẠO / DANH MỤC HỌC PHẦN ---
    # =========================================================

    "Chương trình đào tạo ngành Công nghệ thông tin gồm những học phần nào?",
    "Chương trình đào tạo đại học được cấu trúc như thế nào?",
    "Một chương trình đào tạo cần bao nhiêu tín chỉ để tốt nghiệp?",
    "Các nhóm học phần trong chương trình đào tạo gồm những gì?",
    "Khối kiến thức giáo dục đại cương gồm những học phần nào?",
    "Khối kiến thức cơ sở ngành gồm những học phần nào?",
    "Khối kiến thức chuyên ngành gồm những học phần nào?",
    "Học phần bắt buộc là gì?",
    "Học phần tự chọn là gì?",
    "Sinh viên phải hoàn thành bao nhiêu tín chỉ tự chọn?",
    "Danh mục học phần của ngành Công nghệ thông tin ở đâu?",
    "Điều kiện để đăng ký các học phần chuyên ngành là gì?",
    "Sinh viên có thể thay thế học phần tự chọn bằng học phần khác không?",
    "Các học phần nào là điều kiện tiên quyết của nhau?",
    "Chương trình đào tạo có quy định về thực tập không?",
    "Thực tập tốt nghiệp được thực hiện như thế nào?",
    "Điều kiện để được đăng ký thực tập tốt nghiệp là gì?",
    "Điều kiện để được làm khóa luận tốt nghiệp là gì?",
    "Sinh viên có thể chọn đồ án hoặc khóa luận tốt nghiệp không?",
    "Điều kiện để được đăng ký đồ án tốt nghiệp là gì?",
    "Điều kiện để được đăng ký khóa luận tốt nghiệp là gì?",


    # =========================================================
    # --- THI / KIỂM TRA / TỐT NGHIỆP ---
    # =========================================================

    "Lịch thi cuối kỳ được công bố ở đâu?",
    "Sinh viên xem lịch thi như thế nào?",
    "Nếu bị trùng lịch thi thì phải làm thế nào?",
    "Sinh viên cần mang gì khi đi thi?",
    "Sinh viên có được sử dụng tài liệu khi thi không?",
    "Quy định về các vật dụng được mang vào phòng thi là gì?",
    "Sinh viên đi thi trễ có được vào phòng thi không?",
    "Sinh viên quên thẻ sinh viên khi đi thi phải làm gì?",
    "Sinh viên mất thẻ sinh viên có được dự thi không?",
    "Sinh viên bị ốm trước ngày thi phải làm gì?",
    "Quy định về thi bù trong trường hợp bị ốm như thế nào?",
    "Quy định về vi phạm quy chế thi như thế nào?",
    "Những hành vi nào bị xem là gian lận trong thi cử?",
    "Sinh viên vi phạm quy chế thi bị xử lý như thế nào?",
    "Điều kiện để được xét tốt nghiệp là gì?",
    "Sinh viên cần tích lũy bao nhiêu tín chỉ để được xét tốt nghiệp?",
    "Sinh viên cần hoàn thành những điều kiện nào ngoài tín chỉ?",
    "Điều kiện về giáo dục quốc phòng khi xét tốt nghiệp là gì?",
    "Điều kiện về giáo dục thể chất khi xét tốt nghiệp là gì?",
    "Điều kiện về ngoại ngữ khi xét tốt nghiệp là gì?",
    "Điều kiện về tin học khi xét tốt nghiệp là gì?",
    "Sinh viên có nợ học phần có được xét tốt nghiệp không?",
    "Sinh viên bị nợ học phí có được xét tốt nghiệp không?",
    "Thủ tục đăng ký xét tốt nghiệp như thế nào?",
    "Thời gian đăng ký xét tốt nghiệp là khi nào?",
    "Sinh viên có thể xin hoãn xét tốt nghiệp không?",


    # =========================================================
    # --- ĐIỂM RÈN LUYỆN ---
    # =========================================================

    "Điểm rèn luyện là gì?",
    "Điểm rèn luyện được tính như thế nào?",
    "Các tiêu chí đánh giá điểm rèn luyện gồm những gì?",
    "Mỗi tiêu chí điểm rèn luyện được tính bao nhiêu điểm?",
    "Điểm rèn luyện tối đa là bao nhiêu?",
    "Điểm rèn luyện được đánh giá bao nhiêu lần trong một năm?",
    "Sinh viên tự đánh giá điểm rèn luyện như thế nào?",
    "Sinh viên xem điểm rèn luyện ở đâu?",
    "Thời gian đánh giá điểm rèn luyện là khi nào?",
    "Sinh viên bị trừ điểm rèn luyện trong những trường hợp nào?",
    "Những hành vi nào bị trừ điểm rèn luyện?",
    "Tham gia hoạt động Đoàn Hội có được cộng điểm rèn luyện không?",
    "Tham gia hoạt động tình nguyện có được cộng điểm rèn luyện không?",
    "Tham gia hoạt động phong trào có được cộng điểm rèn luyện không?",
    "Điểm rèn luyện dùng để làm gì?",
    "Điểm rèn luyện có ảnh hưởng đến học bổng không?",
    "Điểm rèn luyện có ảnh hưởng đến xếp loại tốt nghiệp không?",
    "Sinh viên có được khiếu nại điểm rèn luyện không?",
    "Thủ tục khiếu nại điểm rèn luyện như thế nào?",
    "Nếu phát hiện điểm rèn luyện bị tính sai thì phải làm gì?",


    # =========================================================
    # --- KÝ TÚC XÁ ---
    # =========================================================

    "Sinh viên đăng ký ký túc xá như thế nào?",
    "Ký túc xá của Đại học Cần Thơ có những khu nào?",
    "Sinh viên năm nhất có được ưu tiên vào ký túc xá không?",
    "Đối tượng nào được đăng ký ký túc xá?",
    "Điều kiện để được ở ký túc xá là gì?",
    "Sinh viên cần chuẩn bị hồ sơ gì để đăng ký ký túc xá?",
    "Thời gian đăng ký ký túc xá là khi nào?",
    "Đăng ký ký túc xá trực tuyến ở đâu?",
    "Sinh viên có thể đăng ký ký túc xá trực tiếp không?",
    "Một phòng ký túc xá có bao nhiêu sinh viên?",
    "Giá phòng ký túc xá là bao nhiêu?",
    "Phí ký túc xá được tính theo tháng hay học kỳ?",
    "Sinh viên phải đóng những khoản phí nào khi ở ký túc xá?",
    "Tiền điện nước trong ký túc xá được tính như thế nào?",
    "Ký túc xá có cung cấp wifi không?",
    "Ký túc xá có những tiện ích gì?",
    "Sinh viên có được đổi phòng ký túc xá không?",
    "Thủ tục chuyển phòng ký túc xá như thế nào?",
    "Sinh viên muốn trả phòng ký túc xá phải làm gì?",
    "Sinh viên vi phạm nội quy ký túc xá bị xử lý như thế nào?",
    "Những hành vi nào bị cấm trong ký túc xá?",
    "Sinh viên có được đưa khách vào ký túc xá không?",
    "Ký túc xá có quy định giờ đóng mở cổng không?",
    "Sinh viên được phép ở lại ký túc xá trong thời gian nghỉ hè không?",
    "Sinh viên nữ và sinh viên nam được bố trí khu vực như thế nào?",


    # =========================================================
    # --- TÀI KHOẢN / EMAIL / MYCTU / DỊCH VỤ SỐ ---
    # =========================================================

    "Tân sinh viên nhận tài khoản sinh viên như thế nào?",
    "Tài khoản sinh viên dùng để đăng nhập những hệ thống nào?",
    "Sinh viên đăng nhập MyCTU như thế nào?",
    "Sinh viên quên mật khẩu MyCTU phải làm thế nào?",
    "Sinh viên đổi mật khẩu tài khoản như thế nào?",
    "Sinh viên lấy email trường ở đâu?",
    "Email sinh viên Đại học Cần Thơ có dạng như thế nào?",
    "Email sinh viên được sử dụng cho những dịch vụ nào?",
    "Sinh viên quên mật khẩu email phải làm gì?",
    "Sinh viên bị khóa tài khoản phải làm thế nào?",
    "Sinh viên xem thời khóa biểu ở đâu?",
    "Sinh viên xem điểm học tập ở đâu?",
    "Sinh viên xem học phí ở đâu?",
    "Sinh viên đăng ký học phần trực tuyến ở đâu?",
    "Sinh viên xem lịch thi ở đâu?",
    "Sinh viên xem điểm rèn luyện ở đâu?",
    "Sinh viên cập nhật thông tin cá nhân trên hệ thống như thế nào?",
    "Nếu hệ thống MyCTU bị lỗi thì sinh viên liên hệ ai?",
    "Các dịch vụ số dành cho sinh viên gồm những gì?",
    "Sinh viên có thể sử dụng thư viện điện tử như thế nào?",
    "Sinh viên có thể truy cập wifi của trường như thế nào?",
    "Sinh viên đăng nhập mạng wifi trường bằng tài khoản nào?",
    "Sinh viên cần làm gì khi không truy cập được hệ thống học tập?",


    # =========================================================
    # --- BẢO HIỂM Y TẾ ---
    # =========================================================

    "Sinh viên có bắt buộc tham gia bảo hiểm y tế không?",
    "Sinh viên phải đóng bảo hiểm y tế như thế nào?",
    "Mức đóng bảo hiểm y tế của sinh viên là bao nhiêu?",
    "Bảo hiểm y tế sinh viên có thời hạn bao lâu?",
    "Sinh viên có thể đăng ký bảo hiểm y tế ở đâu?",
    "Sinh viên đăng ký bảo hiểm y tế trực tuyến như thế nào?",
    "Sinh viên đã có thẻ bảo hiểm y tế theo hộ gia đình có phải mua lại không?",
    "Sinh viên thuộc diện được Nhà nước hỗ trợ bảo hiểm y tế cần làm gì?",
    "Sinh viên cần cung cấp giấy tờ gì khi đăng ký bảo hiểm y tế?",
    "Sinh viên có thể thay đổi nơi đăng ký khám chữa bệnh ban đầu không?",
    "Sinh viên kiểm tra thời hạn bảo hiểm y tế ở đâu?",
    "Sinh viên bị mất thẻ bảo hiểm y tế phải làm gì?",
    "Thẻ bảo hiểm y tế điện tử có được sử dụng không?",
    "Sinh viên đi khám chữa bệnh bằng bảo hiểm y tế như thế nào?",
    "Sinh viên chuyển trường có phải đăng ký lại bảo hiểm y tế không?",


    # =========================================================
    # --- HỌC BỔNG / HỖ TRỢ TÀI CHÍNH ---
    # =========================================================

    "Đại học Cần Thơ có những loại học bổng nào dành cho sinh viên?",
    "Học bổng khuyến khích học tập là gì?",
    "Điều kiện để được nhận học bổng khuyến khích học tập là gì?",
    "Học bổng khuyến khích học tập được xét như thế nào?",
    "Sinh viên năm nhất có được xét học bổng không?",
    "Điểm trung bình bao nhiêu thì có thể được xét học bổng?",
    "Điểm rèn luyện có ảnh hưởng đến việc xét học bổng không?",
    "Sinh viên nợ học phần có được xét học bổng không?",
    "Có những học bổng doanh nghiệp nào dành cho sinh viên?",
    "Có những học bổng dành cho sinh viên có hoàn cảnh khó khăn không?",
    "Sinh viên có thể nhận nhiều học bổng cùng lúc không?",
    "Sinh viên cần chuẩn bị hồ sơ gì để xin học bổng?",
    "Thời gian nộp hồ sơ học bổng là khi nào?",
    "Sinh viên nộp hồ sơ học bổng ở đâu?",
    "Quy trình xét học bổng diễn ra như thế nào?",
    "Sinh viên có thể xin hỗ trợ tài chính khẩn cấp không?",
    "Trường có chính sách hỗ trợ sinh viên có hoàn cảnh khó khăn không?",
    "Sinh viên thuộc diện chính sách được hưởng những hỗ trợ nào?",
    "Có chính sách miễn giảm học phí cho sinh viên không?",
    "Đối tượng nào được miễn học phí?",
    "Đối tượng nào được giảm học phí?",
    "Hồ sơ xin miễn giảm học phí gồm những gì?",
    "Thời hạn nộp hồ sơ miễn giảm học phí là khi nào?",
    "Sinh viên có thể vay vốn học tập ở đâu?",
    "Sinh viên cần làm thủ tục gì để được vay vốn học tập?",


    # =========================================================
    # --- ĐOÀN - HỘI / CLB / HOẠT ĐỘNG SINH VIÊN ---
    # =========================================================

    "Đoàn trường Đại học Cần Thơ có những hoạt động gì?",
    "Hội Sinh viên trường Đại học Cần Thơ có những hoạt động gì?",
    "Làm sao để tham gia Đoàn Thanh niên?",
    "Làm sao để tham gia Hội Sinh viên?",
    "Sinh viên năm nhất có thể tham gia Đoàn Hội ngay không?",
    "Trường có những câu lạc bộ sinh viên nào?",
    "Sinh viên có thể tham gia câu lạc bộ như thế nào?",
    "Danh sách các câu lạc bộ sinh viên hiện nay gồm những câu lạc bộ nào?",
    "Sinh viên có thể tham gia nhiều câu lạc bộ cùng lúc không?",
    "Tham gia hoạt động Đoàn Hội có được cộng điểm rèn luyện không?",
    "Các hoạt động tình nguyện dành cho sinh viên gồm những gì?",
    "Sinh viên đăng ký hoạt động tình nguyện ở đâu?",
    "Các phong trào sinh viên thường được tổ chức như thế nào?",
    "Sinh viên có thể tham gia chiến dịch tình nguyện hè không?",
    "Sinh viên có thể tham gia Tiếp sức mùa thi không?",
    "Sinh viên có thể tham gia Xuân tình nguyện không?",
    "Trường có hoạt động văn nghệ thể thao nào dành cho sinh viên?",
    "Sinh viên có thể đăng ký tham gia các cuộc thi của trường ở đâu?",
    "Sinh viên muốn thành lập câu lạc bộ cần làm gì?",
    "Quy định đối với câu lạc bộ sinh viên như thế nào?",


    # =========================================================
    # --- QUYỀN / NGHĨA VỤ / NỘI QUY SINH VIÊN ---
    # =========================================================

    "Quyền của sinh viên Đại học Cần Thơ là gì?",
    "Nghĩa vụ của sinh viên Đại học Cần Thơ là gì?",
    "Sinh viên phải chấp hành những quy định nào của nhà trường?",
    "Sinh viên phải tuân thủ những quy định nào khi học tập?",
    "Những hành vi nào sinh viên bị nghiêm cấm?",
    "Sinh viên vi phạm nội quy trường học bị xử lý như thế nào?",
    "Các hình thức kỷ luật sinh viên gồm những gì?",
    "Khi nào sinh viên bị khiển trách?",
    "Khi nào sinh viên bị cảnh cáo?",
    "Khi nào sinh viên bị đình chỉ học tập?",
    "Sinh viên có quyền khiếu nại quyết định kỷ luật không?",
    "Thủ tục khiếu nại quyết định kỷ luật sinh viên như thế nào?",
    "Sinh viên cần làm gì khi bị mất thẻ sinh viên?",
    "Sinh viên cần làm gì khi mất tài sản trong trường?",
    "Sinh viên có được sử dụng phòng học ngoài giờ không?",
    "Sinh viên có thể sử dụng cơ sở vật chất của trường như thế nào?",


    # =========================================================
    # --- SỔ TAY SINH VIÊN ---
    # =========================================================

    "Sổ tay sinh viên quy định những nội dung gì?",
    "Sổ tay sinh viên quy định gì về học vụ?",
    "Sổ tay sinh viên quy định gì về quyền và nghĩa vụ?",
    "Sổ tay sinh viên quy định gì về điểm rèn luyện?",
    "Sổ tay sinh viên quy định gì về học bổng?",
    "Sổ tay sinh viên quy định gì về kỷ luật sinh viên?",
    "Sổ tay sinh viên quy định gì về tốt nghiệp?",
    "Sổ tay sinh viên hướng dẫn sử dụng những dịch vụ nào?",
    "Sổ tay sinh viên có quy định về ký túc xá không?",
    "Sổ tay sinh viên có hướng dẫn về bảo hiểm y tế không?",
    "Sổ tay sinh viên có thông tin về Đoàn Hội và câu lạc bộ không?",


    # =========================================================
    # --- THƯ VIỆN / HỌC LIỆU / CƠ SỞ VẬT CHẤT ---
    # =========================================================

    "Sinh viên sử dụng thư viện như thế nào?",
    "Sinh viên đăng ký tài khoản thư viện ở đâu?",
    "Sinh viên mượn sách thư viện như thế nào?",
    "Sinh viên được mượn tối đa bao nhiêu tài liệu?",
    "Thời gian mượn sách là bao lâu?",
    "Sinh viên trả sách quá hạn bị xử lý như thế nào?",
    "Sinh viên làm mất sách thư viện phải làm gì?",
    "Thư viện có tài liệu điện tử không?",
    "Sinh viên truy cập thư viện điện tử như thế nào?",
    "Sinh viên có thể sử dụng cơ sở dữ liệu học thuật nào của trường?",
    "Sinh viên sử dụng phòng tự học như thế nào?",
    "Trường có những phòng thí nghiệm nào phục vụ sinh viên?",
    "Sinh viên có thể sử dụng phòng máy tính như thế nào?",


    # =========================================================
    # --- HỖ TRỢ SINH VIÊN / TƯ VẤN ---
    # =========================================================

    "Sinh viên cần tư vấn học vụ thì liên hệ ở đâu?",
    "Sinh viên cần hỗ trợ về học phí thì liên hệ ai?",
    "Sinh viên cần hỗ trợ về học bổng thì liên hệ ai?",
    "Sinh viên cần hỗ trợ về ký túc xá thì liên hệ ai?",
    "Sinh viên cần hỗ trợ về bảo hiểm y tế thì liên hệ ai?",
    "Sinh viên cần hỗ trợ về tài khoản sinh viên thì liên hệ ai?",
    "Sinh viên có thể liên hệ phòng công tác sinh viên bằng cách nào?",
    "Sinh viên cần xác nhận giấy tờ ở đâu?",
    "Các loại giấy xác nhận sinh viên có thể xin gồm những loại nào?",
    "Sinh viên xin giấy xác nhận đang học như thế nào?",
    "Sinh viên xin giấy xác nhận sinh viên để làm gì?",
    "Thủ tục xin giấy xác nhận sinh viên gồm những gì?",
    "Sinh viên có thể xin giấy xác nhận trực tuyến không?",
    "Sinh viên xin bảng điểm ở đâu?",
    "Sinh viên xin bảng điểm chính thức như thế nào?",
    "Sinh viên xin giấy xác nhận kết quả học tập như thế nào?",
    "Sinh viên cần liên hệ đâu khi có vấn đề khẩn cấp trong trường?",


    # =========================================================
    # --- CÂU HỎI TRUY NGUỒN TÀI LIỆU ---
    # =========================================================

    "Thông tin này được quy định trong văn bản nào?",
    "Văn bản nào quy định về học phí năm học 2026-2027?",
    "Tên đầy đủ của văn bản quy định về học phí là gì?",
    "Số hiệu văn bản quy định mức học phí là gì?",
    "Văn bản này được ban hành vào ngày nào?",
    "Đơn vị nào ban hành văn bản này?",
    "Văn bản này áp dụng cho những đối tượng sinh viên nào?",
    "Văn bản này áp dụng từ thời điểm nào?",
    "Quy định hiện hành về vấn đề này nằm trong tài liệu nào?",
    "Có tài liệu chính thức nào hướng dẫn nội dung này không?",
    "Tài liệu tham khảo cho câu trả lời này là gì?",
    "Tên file tài liệu nguồn của thông tin này là gì?",
    "Thông tin này nằm ở trang nào của tài liệu?",
    "Chatbot có thể cung cấp tài liệu nguồn của câu trả lời này không?",
    "Có thể tải tài liệu PDF được chatbot sử dụng không?",
    "Có văn bản nào mới hơn thay thế quy định này không?",
    "Quy định này đã hết hiệu lực chưa?",
    "Có văn bản sửa đổi hoặc bổ sung quy định này không?",
    "Quy định hiện tại khác gì so với quy định trước đây?",
    "Bạn có thể liệt kê các tài liệu tham khảo được sử dụng để trả lời câu hỏi này không?",


    # =========================================================
    # --- CÂU HỎI XỬ LÝ TÌNH HUỐNG / EDGE CASE ---
    # =========================================================

    "Nếu sinh viên quên đóng học phí đúng hạn thì phải làm gì?",
    "Nếu sinh viên không đăng ký được học phần thì phải làm gì?",
    "Nếu hệ thống đăng ký học phần bị lỗi thì phải làm gì?",
    "Nếu sinh viên nhập sai thông tin cá nhân thì xử lý như thế nào?",
    "Nếu sinh viên mất thẻ sinh viên thì phải làm gì?",
    "Nếu sinh viên quên mật khẩu tài khoản thì phải làm gì?",
    "Nếu sinh viên bị mất thẻ bảo hiểm y tế thì xử lý như thế nào?",
    "Nếu sinh viên quên nộp hồ sơ đúng hạn thì có được bổ sung không?",
    "Nếu sinh viên không thể tham gia buổi học vì lý do chính đáng thì phải làm gì?",
    "Nếu sinh viên bị trùng lịch thi thì giải quyết như thế nào?",
    "Nếu sinh viên không đủ điều kiện dự thi thì phải làm gì?",
    "Nếu sinh viên muốn học lại một môn đã đạt thì làm như thế nào?",
    "Nếu sinh viên muốn bảo lưu kết quả học tập thì phải làm gì?",
    "Nếu sinh viên muốn quay lại học sau khi bảo lưu thì phải làm gì?",
    "Nếu sinh viên muốn thôi học thì cần thực hiện những bước nào?",
    "Nếu sinh viên muốn chuyển ngành thì cần đáp ứng điều kiện gì?",
    "Nếu sinh viên muốn học cùng lúc hai ngành thì phải làm gì?",
    "Nếu sinh viên gặp khó khăn tài chính thì có những hình thức hỗ trợ nào?",
    "Nếu sinh viên không được xét học bổng thì có thể xem lý do ở đâu?",
    "Nếu điểm rèn luyện bị sai thì có thể yêu cầu điều chỉnh không?",


    # =========================================================
    # --- CÂU HỎI TỔNG HỢP ĐỂ "QUÉT" KHO DỮ LIỆU ---
    # =========================================================

    "Bạn có thể liệt kê toàn bộ các nội dung mà chatbot có thể tư vấn cho tân sinh viên không?",
    "Bạn có thể liệt kê toàn bộ các tài liệu mà chatbot đang sử dụng để tư vấn sinh viên không?",
    "Chatbot hiện có những nhóm tài liệu nào trong cơ sở tri thức?",
    "Có những tài liệu nào liên quan đến học vụ?",
    "Có những tài liệu nào liên quan đến học phí?",
    "Có những tài liệu nào liên quan đến ký túc xá?",
    "Có những tài liệu nào liên quan đến học bổng và hỗ trợ sinh viên?",
    "Có những tài liệu nào liên quan đến bảo hiểm y tế?",
    "Có những tài liệu nào liên quan đến Đoàn Hội và hoạt động sinh viên?",
    "Có những tài liệu nào hướng dẫn sử dụng các hệ thống số của trường?",
    "Những tài liệu nào dành riêng cho tân sinh viên khóa 52?",
    "Những tài liệu nào áp dụng cho toàn bộ sinh viên?",
    "Tài liệu nào là văn bản quy định chính thức?",
    "Tài liệu nào là tài liệu hướng dẫn?",
    "Tài liệu nào là thông báo?",
    "Tài liệu nào là kế hoạch?",
    "Tài liệu nào là sổ tay sinh viên?",
]

OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctu_chatbot_qa.csv")
TIMEOUT_PER_QUESTION = 20      # giây chờ tối đa cho mỗi câu trả lời
DELAY_BETWEEN_QUESTIONS = 2.0  # giây nghỉ giữa các câu hỏi


def ask_question(ws, question: str) -> dict:
    """Gửi 1 câu hỏi qua WebSocket đã kết nối, nhận & ghép các frame stream."""
    ws.send(question)  # frame gửi đi là TEXT THUẦN, không bọc JSON

    full_answer = ""
    sources = []
    start = time.time()

    while time.time() - start < TIMEOUT_PER_QUESTION:
        try:
            ws.settimeout(TIMEOUT_PER_QUESTION)
            raw = ws.recv()
        except websocket.WebSocketTimeoutException:
            break

        if not raw:
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Nếu server thi thoảng gửi frame không phải JSON (ping/keepalive), bỏ qua
            continue

        full_answer += data.get("message", "")

        if data.get("sources"):
            for s in data["sources"]:
                fname = s.get("file_name")
                if fname and fname not in sources:
                    sources.append(fname)

        if data.get("is_complete") is True:
            break

    return {
        "question": question,
        "answer": full_answer.strip(),
        "source_files": "; ".join(sources),
    }


def main():
    results = []

    print(f"Đang kết nối tới {WS_URL[:60]}...")
    ws = websocket.create_connection(WS_URL, timeout=TIMEOUT_PER_QUESTION)
    print("Đã kết nối. Bắt đầu gửi câu hỏi...\n")

    try:
        for i, q in enumerate(QUESTIONS, 1):
            print(f"[{i}/{len(QUESTIONS)}] Hỏi: {q}")
            try:
                result = ask_question(ws, q)
                print(f"    -> Trả lời ({len(result['answer'])} ký tự), "
                      f"nguồn: {result['source_files'] or '(không có)'}")
                results.append(result)
            except Exception as e:
                print(f"    !! Lỗi khi hỏi câu này: {e}")
                results.append({"question": q, "answer": "", "source_files": f"ERROR: {e}"})

            time.sleep(DELAY_BETWEEN_QUESTIONS)
    finally:
        ws.close()

    # Ghi ra CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer", "source_files"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nHoàn tất! Đã lưu {len(results)} cặp Q&A vào:\n{OUTPUT_CSV}")


if __name__ == "__main__":
    main()