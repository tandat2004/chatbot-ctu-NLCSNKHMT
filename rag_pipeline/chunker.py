"""Chia tài liệu Markdown thành các đoạn tri thức (chunk).

Chiến lược:
1. Tách theo heading (#, ##, ###...) -> mỗi section giữ "đường dẫn heading" (breadcrumb).
2. Section quá nhỏ được gộp với section kế bên (cùng nhánh) để chunk đủ ngữ nghĩa.
3. Section quá dài được cắt theo đoạn văn; BẢNG không bị cắt ngang dòng, khi bảng dài
   thì cắt theo hàng và lặp lại dòng tiêu đề bảng ở mỗi chunk.
4. Mỗi chunk được gắn dòng ngữ cảnh "[Tên văn bản › Chương › Điều]" ở đầu để
   embedding "hiểu" chunk thuộc văn bản nào, và LLM trích dẫn được nguồn.
"""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def word_count(s: str) -> int:
    return len(s.split())


# ----------------------------------------------------------------------------
# 1. Tách section theo heading
# ----------------------------------------------------------------------------
def parse_sections(body: str) -> list[tuple[list[str], str]]:
    """Trả về danh sách (đường_dẫn_heading, nội_dung)."""
    sections: list[tuple[list[str], str]] = []
    stack: list[tuple[int, str]] = []
    buf: list[str] = []
    in_fence = False

    def flush() -> None:
        text = "\n".join(buf).strip()
        if text:
            sections.append(([t for _, t in stack], text))
        buf.clear()

    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else HEADING_RE.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        else:
            buf.append(line)
    flush()
    return sections


# ----------------------------------------------------------------------------
# 2. Gộp section nhỏ
# ----------------------------------------------------------------------------
def _common_prefix(paths: list[list[str]]) -> list[str]:
    prefix: list[str] = []
    for parts in zip(*paths):
        if all(p == parts[0] for p in parts):
            prefix.append(parts[0])
        else:
            break
    return prefix


def _build_group(items: list[tuple[list[str], str]]) -> tuple[list[str], str]:
    if len(items) == 1:
        return items[0]
    prefix = _common_prefix([p for p, _ in items])
    parts = []
    for path, text in items:
        extra = path[len(prefix):]
        parts.append((f"**{' › '.join(extra)}**\n" if extra else "") + text)
    return prefix, "\n\n".join(parts)


def merge_small_sections(sections, max_words: int, min_words: int):
    groups = []
    pending: list[tuple[list[str], str]] = []

    def wc(items) -> int:
        return sum(word_count(t) for _, t in items)

    for path, text in sections:
        if pending:
            same_branch = path[:2] == pending[0][0][:2]
            too_big = wc(pending) + word_count(text) > max_words
            if wc(pending) >= min_words or too_big or not same_branch:
                groups.append(_build_group(pending))
                pending = []
        pending.append((path, text))
    if pending:
        groups.append(_build_group(pending))
    return groups


# ----------------------------------------------------------------------------
# 3. Cắt section dài
# ----------------------------------------------------------------------------
def _to_blocks(text: str) -> list[str]:
    blocks, cur = [], []
    for line in text.splitlines():
        if not line.strip():
            if cur:
                blocks.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def _is_table(block: str) -> bool:
    lines = block.splitlines()
    return len(lines) >= 2 and all(l.lstrip().startswith("|") for l in lines)


def _split_table(block: str, budget: int) -> list[str]:
    lines = block.splitlines()
    header, rows = lines[:2], lines[2:]
    header_txt = "\n".join(header)
    out, cur, n = [], [], word_count(header_txt)
    for r in rows:
        w = word_count(r)
        if cur and n + w > budget:
            out.append("\n".join(header + cur))
            cur, n = [], word_count(header_txt)
        cur.append(r)
        n += w
    if cur:
        out.append("\n".join(header + cur))
    return out or [block]


def _hard_split(s: str, budget: int) -> list[str]:
    words = s.split()
    return [" ".join(words[i:i + budget]) for i in range(0, len(words), budget)]


def _split_long_block(block: str, budget: int) -> list[str]:
    units: list[str] = []
    for line in block.splitlines():
        if word_count(line) <= budget:
            units.append(line)
        else:
            for sent in re.split(r"(?<=[.;!?])\s+", line):
                units.extend(_hard_split(sent, budget))
    out, cur, n = [], [], 0
    for u in units:
        w = word_count(u)
        if cur and n + w > budget:
            out.append("\n".join(cur))
            cur, n = [], 0
        cur.append(u)
        n += w
    if cur:
        out.append("\n".join(cur))
    return out


def split_text(text: str, budget: int, overlap: int) -> list[str]:
    if word_count(text) <= budget:
        return [text]
    blocks: list[str] = []
    for b in _to_blocks(text):
        if word_count(b) <= budget:
            blocks.append(b)
        elif _is_table(b):
            blocks.extend(_split_table(b, budget))
        else:
            blocks.extend(_split_long_block(b, budget))

    chunks: list[str] = []
    cur: list[str] = []
    n = 0
    for b in blocks:
        w = word_count(b)
        if cur and n + w > budget:
            chunks.append("\n\n".join(cur))
            last = cur[-1]
            # chồng lấn: mang theo block cuối nếu nhỏ và không phải bảng
            if word_count(last) <= overlap and not _is_table(last) and word_count(last) + w <= budget:
                cur, n = [last], word_count(last)
            else:
                cur, n = [], 0
        cur.append(b)
        n += w
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


# ----------------------------------------------------------------------------
# API chính
# ----------------------------------------------------------------------------
def chunk_markdown(body: str, doc_title: str, max_words: int = 280,
                   min_words: int = 40, overlap_words: int = 40,
                   doc_label: str | None = None) -> list[dict]:
    """Trả về list[{'text': ..., 'section': ...}].

    `doc_label` là nhãn hiển thị ở dòng ngữ cảnh đầu chunk (mặc định = doc_title);
    thường là "Tên văn bản (số hiệu)" để tìm theo số hiệu cũng ra.
    """
    from textutil import norm_key

    sections = parse_sections(body)
    if not sections and body.strip():
        sections = [([], body.strip())]
    groups = merge_small_sections(sections, max_words, min_words)

    out: list[dict] = []
    title_key = norm_key(doc_title)
    for path, text in groups:
        crumb = " › ".join(p for p in path if norm_key(p) != title_key)
        header = f"[{doc_label or doc_title}" + (f" › {crumb}" if crumb else "") + "]"
        budget = max(max_words - word_count(header), 80)
        for piece in split_text(text, budget, overlap_words):
            out.append({"text": f"{header}\n{piece}", "section": crumb})
    return out
