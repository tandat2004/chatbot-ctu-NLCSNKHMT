"""Chạy bộ câu hỏi test (test_questions.json) qua chatbot, ghi báo cáo Markdown.

Dùng để phục vụ mục "Kiểm thử chất lượng câu trả lời" (bước 3) và làm số liệu
thực nghiệm cho báo cáo cuối kỳ (bước 5).

Cách dùng:
    python eval_qa.py                                  # dùng test_questions.json mặc định
    python eval_qa.py --questions my_questions.json
    python eval_qa.py --out eval_results.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from generate import Answerer
from search import KnowledgeBase


def run(questions_path: Path, out_path: Path, k: int) -> None:
    items = json.loads(questions_path.read_text(encoding="utf-8"))

    kb = KnowledgeBase()
    bot = Answerer(kb)

    lines = [f"# Kết quả kiểm thử chatbot — {len(items)} câu hỏi\n"]
    total_t = 0.0
    low_conf_count = 0

    for i, item in enumerate(items, 1):
        q, topic = item["question"], item.get("topic")
        topics = [topic] if topic else None
        print(f"[{i}/{len(items)}] {q}")

        t0 = time.time()
        result = bot.answer(q, k=k, topics=topics)
        dt = time.time() - t0
        total_t += dt
        if result.low_confidence:
            low_conf_count += 1

        lines.append(f"## {item['id']} — {q}")
        if item.get("notes"):
            lines.append(f"> Ghi chú: {item['notes']}")
        lines.append(f"\n**Trả lời** ({dt:.1f}s, low_confidence={result.low_confidence}):\n")
        lines.append(result.text)
        if result.hits:
            src = "; ".join(
                f"[{n}] {h.metadata.get('doc_title', h.metadata.get('source_file', ''))}"
                for n, h in enumerate(result.hits, 1)
            )
            lines.append(f"\n**Nguồn:** {src}")
        lines.append("\n**Đánh giá thủ công:** ☐ Đúng &nbsp;&nbsp; ☐ Sai &nbsp;&nbsp; ☐ Thiếu sót\n")
        lines.append("---\n")

    summary = (
        f"\n## Tổng kết\n"
        f"- Tổng số câu hỏi: {len(items)}\n"
        f"- Thời gian trung bình / câu: {total_t / len(items):.1f}s\n"
        f"- Số câu low_confidence: {low_conf_count}/{len(items)}\n"
        f"- Còn thiếu để hoàn tất: điền cột **Đánh giá thủ công** ở trên sau khi đối chiếu với quy định gốc.\n"
    )
    lines.insert(1, summary)

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✔ Đã ghi {out_path.resolve()} — mở ra để chấm thủ công từng câu.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--questions", type=Path, default=Path("test_questions.json"))
    ap.add_argument("--out", type=Path, default=Path("eval_results.md"))
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args()
    run(args.questions, args.out, args.k)


if __name__ == "__main__":
    main()
