"""Sinh câu trả lời bằng OpenAI GPT, dựa trên ngữ cảnh lấy từ KnowledgeBase (search.py).

Cần biến môi trường OPENAI_API_KEY.
Cài đặt: pip install openai --break-system-packages   (cần bản openai >= 1.0)

Dùng như thư viện:
    from search import KnowledgeBase
    from generate import Answerer

    kb = KnowledgeBase()
    bot = Answerer(kb)
    result = bot.answer("Học phí học kỳ 1 đóng khi nào?")
    print(result.text)
    for h in result.hits:
        print(h.metadata.get("source_file"))

Dùng dòng lệnh:
    python generate.py "học phí học kỳ 1 đóng khi nào?"
    python generate.py --topic hoc_phi
    python generate.py                       # chế độ hỏi-đáp tương tác
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

import config
from search import Hit, KnowledgeBase

# Tự động đọc file .env ở thư mục gốc project (nếu có), nạp OPENAI_API_KEY
# vào biến môi trường của tiến trình hiện tại. Nếu file không tồn tại, không báo lỗi.
load_dotenv()

SYSTEM_PROMPT = """Bạn là trợ lý ảo của Trường Đại học Cần Thơ (CTU), trả lời câu hỏi của sinh viên \
về quy định học vụ CHỈ DỰA TRÊN các đoạn trích trong phần "Ngữ cảnh" được cung cấp.

Quy tắc bắt buộc:
- Chỉ dùng thông tin có trong Ngữ cảnh. Không bịa, không suy đoán thêm quy định không có trong đó.
- Nếu Ngữ cảnh không đủ để trả lời, hãy nói rõ là bạn chưa tìm thấy quy định liên quan và gợi ý \
sinh viên hỏi lại cụ thể hơn hoặc liên hệ phòng ban phù hợp.
- Khi dùng thông tin từ một đoạn, trích số nguồn tương ứng trong ngoặc vuông, ví dụ [1], [2].
- Nếu đoạn nào có cảnh báo "HẾT HIỆU LỰC" hoặc "cần kiểm tra lại", PHẢI nhắc rõ điều đó trong câu \
trả lời thay vì bỏ qua.
- Trả lời ngắn gọn, đúng trọng tâm, bằng tiếng Việt, giọng thân thiện, dễ hiểu với sinh viên."""

ANSWER_PROMPT_TEMPLATE = """Ngữ cảnh:
{context}

Câu hỏi: {question}

Trả lời (nhớ trích nguồn dạng [n]):"""

NO_CONTEXT_MSG = (
    "Mình không tìm thấy quy định liên quan trong cơ sở dữ liệu hiện có. "
    "Bạn thử hỏi cụ thể hơn hoặc liên hệ phòng ban phụ trách nhé."
)

# Model mặc định nếu config.py chưa khai báo OPENAI_MODEL riêng.
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


@dataclass
class Answer:
    text: str
    hits: list[Hit]
    low_confidence: bool = False


class Answerer:
    def __init__(self, kb: KnowledgeBase, model: Optional[str] = None, api_key: Optional[str] = None):
        from openai import OpenAI

        self.kb = kb
        # Ưu tiên: model truyền vào > config.OPENAI_MODEL (nếu có) > mặc định
        self.model = model or getattr(config, "OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise SystemExit("Thiếu OPENAI_API_KEY. Đặt biến môi trường hoặc truyền api_key=... khi khởi tạo Answerer.")
        self.client = OpenAI(api_key=key)

    def answer(
        self,
        question: str,
        k: int = config.DEFAULT_TOP_K,
        topics: Optional[list[str]] = None,
        chunk_type: Optional[str] = None,
        hybrid: bool = True,
    ) -> Answer:
        hits = self.kb.search(question, k=k, topics=topics, chunk_type=chunk_type, hybrid=hybrid)
        if not hits:
            return Answer(text=NO_CONTEXT_MSG, hits=[], low_confidence=True)

        context = self.kb.format_context(hits)
        prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=question)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=config.LLM_TEMPERATURE,
        )
        text = (response.choices[0].message.content or "").strip()
        low_conf = all(h.low_confidence for h in hits)
        return Answer(text=text, hits=hits, low_confidence=low_conf)


def _print_answer(result: Answer) -> None:
    print(f"\n🤖 {result.text}\n")
    if result.low_confidence and result.hits:
        print("  ⚠ Độ tin cậy thấp — kiểm tra lại với nguồn chính thức.")
    if result.hits:
        print("  Nguồn tham khảo:")
        for n, h in enumerate(result.hits, 1):
            m = h.metadata
            tag = m.get("so_hieu") or m.get("source_file", "")
            print(f"   [{n}] {m.get('doc_title', m.get('source_file', ''))}" + (f" — {tag}" if tag else ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question", nargs="?", help="Câu hỏi; bỏ trống để vào chế độ tương tác")
    ap.add_argument("-k", type=int, default=config.DEFAULT_TOP_K)
    ap.add_argument("--topic", action="append", help="Lọc theo chủ đề (có thể lặp lại)")
    ap.add_argument("--type", choices=["faq", "doc"], dest="chunk_type")
    ap.add_argument("--no-hybrid", action="store_true", help="Chỉ dùng tìm kiếm ngữ nghĩa")
    ap.add_argument("--vector-dir", type=Path, default=config.VECTOR_DIR)
    ap.add_argument("--model", default=None, help="Ghi đè model OpenAI (mặc định: config.OPENAI_MODEL hoặc gpt-4o-mini)")
    args = ap.parse_args()

    kb = KnowledgeBase(args.vector_dir)
    bot = Answerer(kb, model=args.model)
    run = lambda q: _print_answer(  # noqa: E731
        bot.answer(q, args.k, args.topic, args.chunk_type, not args.no_hybrid)
    )

    if args.question:
        run(args.question)
        return

    print("Nhập câu hỏi (Enter trống để thoát).")
    while True:
        q = input("\n❓ ").strip()
        if not q:
            break
        run(q)


if __name__ == "__main__":
    main()