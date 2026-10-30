"""
evaluate_rag.py — Kiểm thử chất lượng câu trả lời RAG cho Giai đoạn 3
Chạy: python rag_pipeline/evaluate_rag.py
"""
import sys, time
sys.path.insert(0, 'rag_pipeline')
from dotenv import load_dotenv
load_dotenv('.env')
from generate import KnowledgeBase, Answerer

TEST_CASES = [
    {"category": "Quy chế học vụ",  "question": "Sinh viên bị cảnh báo học vụ khi nào?",            "expect_src": "QD3266"},
    {"category": "Học phí",          "question": "Học phí học lại một tín chỉ là bao nhiêu?",         "expect_src": "HocPhi"},
    {"category": "Biểu mẫu thi",    "question": "Đơn xin hoãn thi kết thúc học phần dùng mẫu nào?", "expect_src": "BM_08"},
    {"category": "Ký túc xá",        "question": "Thủ tục đăng ký nội trú ký túc xá gồm những bước nào?","expect_src": "ktx"},
    {"category": "Học bổng",         "question": "Điều kiện để được xét học bổng khuyến khích học tập?","expect_src": "hoc_bong"},
    {"category": "Điểm rèn luyện",  "question": "Cách tính điểm rèn luyện học kỳ như thế nào?",     "expect_src": "ren_luyen"},
    {"category": "Đoàn - Hội",      "question": "5 tiêu chí xét đạt danh hiệu Sinh viên 5 tốt?",    "expect_src": "5tot"},
]

def run_evaluation():
    kb = KnowledgeBase()
    bot = Answerer(kb, provider='groq')

    print(f"\n{'='*75}", flush=True)
    print(f" ĐÁNH GIÁ CHẤT LƯỢNG RAG — CTU Chatbot | Provider: {bot.provider} | Model: {bot.model}", flush=True)
    print(f"{'='*75}", flush=True)
    print(f"{'#':<3} | {'Chủ đề':<20} | {'ms':<7} | {'Trích dẫn':<11} | {'Nguồn top-1':<40}", flush=True)
    print(f"{'-'*3}-+-{'-'*20}-+-{'-'*7}-+-{'-'*11}-+-{'-'*40}", flush=True)

    passed = 0
    for idx, tc in enumerate(TEST_CASES, 1):
        t0 = time.time()
        ans = bot.answer(tc['question'], k=5)
        ms = int((time.time() - t0) * 1000)

        has_citation = '[1]' in ans.text or '[2]' in ans.text or '[3]' in ans.text
        top_src = ans.hits[0].metadata.get('source_file', 'N/A')[:40] if ans.hits else 'N/A'
        status = '✅ Đạt' if has_citation else '⚠️  Thiếu trích dẫn'

        if has_citation:
            passed += 1
        print(f"{idx:<3} | {tc['category']:<20} | {ms:<7} | {status:<13} | {top_src}", flush=True)

    print(f"\n{'='*75}", flush=True)
    print(f"Kết quả: {passed}/{len(TEST_CASES)} câu có trích dẫn nguồn đầy đủ", flush=True)
    if passed == len(TEST_CASES):
        print("✅  HỆ THỐNG ĐẠT CHUẨN TRÍCH DẪN 100%")
    else:
        print(f"⚠️   Còn {len(TEST_CASES)-passed} câu thiếu trích dẫn — kiểm tra lại System Prompt")

if __name__ == '__main__':
    run_evaluation()
