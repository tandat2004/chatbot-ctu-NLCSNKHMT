"""Tìm chữ tiếng Việt bị dính vào nhau (vd "biệtmột", "tiêuchuẩn") trong các file sẽ được đưa vào chỉ mục.

Nguyên lý: mỗi âm tiết tiếng Việt có cấu trúc [phụ âm đầu] + [nguyên âm] + [phụ âm cuối].
Một "từ" viết liền mà không khớp cấu trúc đó (vd "biệt"+"một") gần như chắc chắn là 2 từ bị dính.

Cách dùng:
    python check_glued_words.py --data-dir ../Data_CTU_restructured
    python check_glued_words.py --data-dir ... --all      # quét cả file không nằm trong chỉ mục

Chỉ BÁO CÁO, không tự sửa. Kết quả đầy đủ ghi vào glued_words_report.txt.
Gợi ý tách chỉ mang tính tham khảo — hãy đối chiếu với văn bản gốc trước khi sửa.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

TONE_MARKS = {"\u0300", "\u0301", "\u0303", "\u0309", "\u0323"}  # huyền sắc ngã hỏi nặng
SYLLABLE_RE = re.compile(
    r"(?:ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdđghklmnpqrstvx])?"   # phụ âm đầu
    r"[aăâeêioôơuưy]+"                                              # nguyên âm
    r"(?:ch|ng|nh|[cmnpt])?"                                        # phụ âm cuối
)
WORD_RE = re.compile(r"[^\W\d_]+")  # chuỗi chữ cái liên tục


def _base(token: str) -> str:
    """Bỏ dấu thanh, giữ nguyên ă â ê ô ơ ư đ."""
    d = unicodedata.normalize("NFD", token.lower())
    d = "".join(c for c in d if c not in TONE_MARKS)
    return unicodedata.normalize("NFC", d)


def is_syllable(token: str) -> bool:
    return bool(SYLLABLE_RE.fullmatch(_base(token)))


def segment(token: str, max_parts: int = 4):
    """Thử tách `token` thành các âm tiết hợp lệ (quy hoạch động). Trả về list hoặc None."""
    n = len(token)
    best: list = [None] * (n + 1)
    best[0] = []
    for i in range(1, n + 1):
        for j in range(max(0, i - 7), i):  # âm tiết dài nhất ~7 chữ cái
            if best[j] is not None and is_syllable(token[j:i]):
                cand = best[j] + [token[j:i]]
                if best[i] is None or len(cand) < len(best[i]):
                    best[i] = cand
    seg = best[n]
    return seg if seg and 2 <= len(seg) <= max_parts else None


# Từ phiên âm/tên riêng hợp lệ, không phải lỗi (viết thường). Thêm bằng --allow.
ALLOW = {"lênin", "mácxít"}


def suspicious_tokens(line: str, allow=frozenset()):
    """Sinh (token, gợi_ý_tách, loại) cho các từ nghi bị dính. loại: 'dính' hoặc 'OCR?'."""
    line = unicodedata.normalize("NFC", line)  # tránh vỡ từ khi file ở dạng NFD
    for m in WORD_RE.finditer(line):
        tok = m.group()
        if len(tok) < 5 or tok.isupper() or tok.isascii():   # bỏ viết tắt và từ không dấu/tiếng Anh
            continue
        if tok.lower() in ALLOW or tok.lower() in allow or is_syllable(tok):
            continue
        # token gồm nhiều âm tiết hợp lệ dính nhau => nghi ngờ
        seg = segment(tok)
        if seg:
            # có mảnh 1 chữ cái hoặc chữ hoa nằm giữa từ: nhiều khả năng là ký tự bị OCR sai
            mixed = any(a.islower() and b.isupper() for a, b in zip(tok, tok[1:]))
            ocr = mixed or any(len(x) == 1 for x in seg)
            yield tok, " ".join(seg), "OCR?" if ocr else "dính"


def strip_noise(line: str) -> str:
    line = re.sub(r"`[^`]*`", " ", line)              # code inline
    line = re.sub(r"https?://\S+|\S+@\S+", " ", line)  # URL/email
    return line


def files_to_scan(data_dir: Path, scan_all: bool):
    for p in sorted((data_dir / "processed").rglob("*")):
        if p.suffix.lower() in {".md", ".txt"} and not p.name.lower().startswith(("readme", "_")):
            yield p
    faq = data_dir / "faq"
    if faq.exists():
        for p in sorted(faq.glob("*.md")):
            if scan_all or (p.stem.lower().startswith("faq") and p.stem.lower() != "faq_template"):
                yield p


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--all", action="store_true", help="Quét cả file trong faq/ không bắt đầu bằng 'faq'")
    ap.add_argument("--allow", nargs="*", default=[], help="Từ hợp lệ cần bỏ qua (vd: --allow lênin)")
    ap.add_argument("--show", type=int, default=15, help="Số từ (khác nhau) hiển thị mỗi file")
    args = ap.parse_args()
    allow = {w.lower() for w in args.allow}

    report, total, nfd_files = [], 0, []
    print(f"{'File':<62}{'Nghi ngờ':>9}")
    for p in files_to_scan(args.data_dir, args.all):
        raw_text = p.read_text(encoding="utf-8-sig", errors="replace")
        if not unicodedata.is_normalized("NFC", raw_text):
            nfd_files.append(p.relative_to(args.data_dir).as_posix())
        found: dict[str, dict] = {}
        for ln, line in enumerate(unicodedata.normalize("NFC", raw_text).splitlines(), 1):
            for tok, sug, kind in suspicious_tokens(strip_noise(line), allow):
                e = found.setdefault(tok, {"sug": sug, "kind": kind, "lines": []})
                e["lines"].append(ln)
        n = sum(len(e["lines"]) for e in found.values())
        total += n
        rel = p.relative_to(args.data_dir).as_posix()
        print(f"{rel:<62}{n:>9}")
        if found:
            report.append(f"\n===== {rel} ({n} lần, {len(found)} từ khác nhau) =====")
            for tok, e in sorted(found.items(), key=lambda kv: kv[1]["lines"][0]):
                ls = ",".join(map(str, e["lines"][:12])) + ("..." if len(e["lines"]) > 12 else "")
                report.append(f"  [{e['kind']}] '{tok}' -> '{e['sug']}'   x{len(e['lines'])}   dòng {ls}")
            for tok, e in sorted(found.items(), key=lambda kv: kv[1]["lines"][0])[: args.show]:
                print(f"     [{e['kind']}] {tok!r} -> {e['sug']!r}  x{len(e['lines'])}  dòng {e['lines'][0]}")
    Path("glued_words_report.txt").write_text("\n".join(report), encoding="utf-8")
    print(f"\nTổng cộng {total} lần nghi lỗi. Chi tiết: {Path('glued_words_report.txt').resolve()}")
    if nfd_files:
        print(f"\nLƯU Ý: {len(nfd_files)} file dùng Unicode dạng phân rã (NFD): " + ", ".join(nfd_files))
        print("build_index.py tự chuẩn hóa về NFC khi đọc, nên tìm kiếm không bị ảnh hưởng; "
              "nhưng Ctrl+F/Ctrl+H trong trình soạn thảo có thể không khớp chữ có dấu.")


if __name__ == "__main__":
    main()
