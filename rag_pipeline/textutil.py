"""Tiện ích xử lý văn bản dùng chung."""
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Optional

_STOPWORDS = {
    "la", "va", "cua", "co", "khong", "cho", "cac", "nhung", "mot", "duoc",
    "de", "trong", "voi", "the", "nao", "thi", "khi", "nay", "do", "o", "vao",
}


def strip_accents(s: str) -> str:
    """Bỏ dấu tiếng Việt (kể cả đ/Đ)."""
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def norm_key(s: str) -> str:
    """Chuẩn hóa tên file để so khớp: bỏ dấu, chữ thường, chỉ giữ a-z0-9."""
    return re.sub(r"[^a-z0-9]", "", strip_accents(s).lower())


def tokenize(text: str) -> list[str]:
    """Token hóa cho BM25: bỏ dấu + unigram + bigram.

    Bỏ dấu giúp khớp cả khi người dùng gõ 'hoc phi' thay vì 'học phí'.
    Bigram bắt các từ ghép tiếng Việt ('hoc_phi', 'ky_tuc').
    """
    words = [w for w in re.findall(r"\w+", strip_accents(text).lower())]
    uni = [w for w in words if w not in _STOPWORDS]
    bi = [f"{a}_{b}" for a, b in zip(words, words[1:])]
    return uni + bi


def parse_date(value) -> Optional[date]:
    """Đọc 'YYYY-MM-DD'; trả None nếu rỗng/không hợp lệ."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
