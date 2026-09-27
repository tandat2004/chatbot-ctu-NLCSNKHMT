"""Đọc file FAQ thành các cặp (câu hỏi, trả lời, faq_id).

Các định dạng được hỗ trợ (thử lần lượt):
  A. Có nhãn (định dạng chuẩn của dự án):
         ### FAQ-HP-001
         **❓ Câu hỏi:** ...
         **💬 Trả lời:**
         ...
     cũng nhận "Q:/A:", "**Câu hỏi:**/**Trả lời:**", và
         **1. Câu hỏi?**
         Trả lời: ...
  B. Heading là câu hỏi (kết thúc bằng '?'), nội dung bên dưới là câu trả lời
  C. Bảng có tiêu đề cột "Câu hỏi | Trả lời"
"""
from __future__ import annotations

import re

from chunker import parse_sections

Q_RE = re.compile(r"^(?:Q|Câu\s*hỏi|Câu)\s*\d*\s*[:.)]\s*(.+)$", re.I)
A_RE = re.compile(r"^(?:A|Trả\s*lời|Đáp\s*án|Đáp)\s*[:.)]\s*(.*)$", re.I)
BOLD_NUM_Q_RE = re.compile(r"^\s*\*\*\s*\d+\s*[.)]\s*(.+?)\s*\*\*\s*$")
FAQ_ID_RE = re.compile(r"^#{1,6}\s*(FAQ[-_][\w-]+)\s*$", re.I)
HEADING_RE = re.compile(r"^#{1,6}\s")
SEPARATOR_RE = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")
QUESTION_HEADING_RE = re.compile(r"(\?\s*$)|^(?:Q|Câu\s*hỏi|Câu)\s*\d*\s*[:.)]", re.I)
Q_HDR = re.compile(r"câu\s*hỏi|question", re.I)
A_HDR = re.compile(r"trả\s*lời|đáp|answer", re.I)


def _clean(line: str) -> str:
    """Bỏ ký hiệu markdown và emoji đầu dòng để nhận diện nhãn (chỉ dùng để so khớp)."""
    s = line.strip()
    s = re.sub(r"^(?:#{1,6}\s*|[-*+]\s+|>\s*)+", "", s)
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"^[^\w]+", "", s)  # bỏ emoji/ký hiệu đầu dòng: ❓ 💬 ...
    return s.strip()


def _parse_labeled(text: str) -> list[tuple[str, str, str]]:
    pairs: list[tuple[str, str, str]] = []
    q: list[str] = []
    a: list[str] = []
    mode = None
    fid = ""

    def flush() -> None:
        if q and a and "\n".join(a).strip():
            pairs.append((" ".join(q).strip(), "\n".join(a).strip(), fid))

    for raw in text.splitlines():
        stripped = raw.strip()
        if SEPARATOR_RE.match(stripped):
            continue
        mid = FAQ_ID_RE.match(stripped)
        if mid:                                   # "### FAQ-HP-001": ranh giới giữa 2 cặp
            flush()
            q, a, mode, fid = [], [], None, mid.group(1)
            continue
        cleaned = _clean(raw)
        mq = Q_RE.match(cleaned)
        if HEADING_RE.match(stripped) and not mq:  # heading khác: kết thúc cặp hiện tại
            flush()
            q, a, mode = [], [], None
            continue
        mb = BOLD_NUM_Q_RE.match(raw)
        # trong phần trả lời, mục in đậm có số chỉ được coi là câu hỏi nếu kết thúc bằng '?'
        if mb and (mode != "a" or mb.group(1).rstrip().endswith("?")):
            flush()
            q, a, mode = [mb.group(1).strip()], [], "q"
            continue
        if mq:
            flush()
            q, a, mode = [mq.group(1).strip()], [], "q"
            continue
        ma = A_RE.match(cleaned)
        if ma and mode in ("q", "a"):
            mode = "a"
            if ma.group(1).strip():
                a.append(ma.group(1).strip())
        elif mode == "q" and cleaned:
            q.append(cleaned)
        elif mode == "a":
            a.append(raw.rstrip())
    flush()
    return pairs


def _parse_headings(text: str) -> list[tuple[str, str, str]]:
    pairs = []
    for path, body in parse_sections(text):
        if not path or not QUESTION_HEADING_RE.search(path[-1]):
            continue
        question = re.sub(r"^(?:Q|Câu\s*hỏi|Câu)\s*\d*\s*[:.)]\s*", "", path[-1], flags=re.I).strip()
        answer = re.sub(r"^\**\s*(?:Trả\s*lời|Đáp\s*án|A)\s*[:.)]\s*\**\s*", "", body.strip(), flags=re.I)
        if question and answer:
            pairs.append((question, answer.strip(), ""))
    return pairs


def _parse_table(text: str) -> list[tuple[str, str, str]]:
    rows = [l for l in text.splitlines() if l.strip().startswith("|")]
    if len(rows) < 3:
        return []
    header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    # chỉ nhận bảng có tiêu đề cột đúng dạng "Câu hỏi | Trả lời" (tránh nhầm bảng dữ liệu)
    if not (len(header) >= 2 and Q_HDR.search(header[0]) and any(A_HDR.search(h) for h in header[1:])):
        return []
    pairs = []
    for l in rows[1:]:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) < 2 or all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        q, a = cells[0].replace("**", ""), " | ".join(cells[1:]).replace("<br>", "\n")
        if q and a:
            pairs.append((q, a, ""))
    return pairs


def parse_faq(text: str) -> list[tuple[str, str, str]]:
    for parser in (_parse_labeled, _parse_headings, _parse_table):
        pairs = parser(text)
        if pairs:
            seen, out = set(), []
            for q, a, fid in pairs:  # loại trùng câu hỏi
                if q not in seen:
                    seen.add(q)
                    out.append((q, a, fid))
            return out
    return []


def faq_header_info(text: str) -> dict:
    """Đọc dòng '> Nguồn tham khảo: ...' ở đầu file FAQ (nếu có)."""
    m = re.search(r"^>\s*Nguồn tham khảo\s*:\s*(.+)$", text, re.M)
    return {"nguon_tham_khao": m.group(1).replace("`", "").strip() if m else ""}
