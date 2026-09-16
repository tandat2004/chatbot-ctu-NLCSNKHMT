import json
import re
from pathlib import Path

RAW_DIR = Path(r"D:\Computer Science\NLCSNKHMT\chatbot-ctu-NLCSNKHMT\Data_CTU_restructured\raw")
PROCESSED_DIR = Path(r"D:\Computer Science\NLCSNKHMT\chatbot-ctu-NLCSNKHMT\Data_CTU_restructured\processed")

# Ánh xạ tên thư mục -> topic chuẩn (theo README đã định nghĩa)
TOPIC_MAP = {
    "handbook": "handbook",
    "hoc_vu": "hoc_vu",
    "dang_ky_hoc_phan": "dang_ky_hoc_phan",
    "hoc_phi": "hoc_phi",
    "ktx": "ktx",
    "hoc_bong_ctsv": "hoc_bong_ctsv",
    "danh_muc_nganh": "danh_muc_nganh",
    "diem_ren_luyen": "diem_ren_luyen",
    "doan_hoi": "doan_hoi",
}

# Cấp ban hành suy theo pattern số hiệu (dò được thì ưu tiên, không thì để trống)
def guess_cap_ban_hanh(text: str) -> str:
    if "ĐHCT" in text or "Đại học Cần Thơ" in text:
        return "Trường ĐHCT"
    if "BGDĐT" in text or "Bộ Giáo dục" in text:
        return "Bộ GD&ĐT"
    if "TTg" in text or "Thủ tướng" in text or "Chính phủ" in text:
        return "Thủ tướng / Chính phủ"
    return "CẦN_ĐIỀN"

def find_so_hieu(text: str) -> str:
    # Bắt các mẫu: "Số: 3266 /QĐ-ĐHCT", "Số: 09/2022/QĐ-TTg", "Số: 05/2022/QĐ-TTg"
    m = re.search(r"Số:\s*([0-9]+[\/\s]*[A-ZĐ0-9\-\/]+)", text)
    if m:
        return re.sub(r"\s+", "", m.group(1))
    return "CẦN_ĐIỀN"

def find_ngay_ban_hanh(text: str) -> str:
    # Bắt mẫu "ngày 15 tháng 8 năm 2024"
    m = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", text)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    return "CẦN_ĐIỀN"

def find_tieu_de(text: str) -> str:
    # Lấy dòng có chữ "Quy định" / "Quyết định về" gần đầu văn bản
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 15 and ("Quy định" in line or "Quyết định" in line or "QUYẾT ĐỊNH" in line.upper()):
            return line
    return "CẦN_ĐIỀN"

def build_meta(pdf_path: Path, topic: str) -> dict:
    processed_path = (PROCESSED_DIR / pdf_path.relative_to(RAW_DIR)).with_suffix(".md")
    text = processed_path.read_text(encoding="utf-8") if processed_path.exists() else ""

    return {
        "filename": pdf_path.name,
        "topic": topic,
        "so_hieu": find_so_hieu(text),
        "tieu_de": find_tieu_de(text),
        "source_url": "CẦN_ĐIỀN",
        "cap_ban_hanh": guess_cap_ban_hanh(text),
        "hieu_luc_tu": find_ngay_ban_hanh(text),
        "hieu_luc_den": None,
        "hoc_ky_ap_dung": "CẦN_ĐIỀN",
        "kiem_tra_lai_vao": "CẦN_ĐIỀN",
        "ghi_chu": "",
    }

def run():
    count = 0
    for topic_dir, topic in TOPIC_MAP.items():
        folder = RAW_DIR / topic_dir
        if not folder.exists():
            continue
        for f in list(folder.glob("*.pdf")) + list(folder.glob("*.docx")):
            meta = build_meta(f, topic)
            meta_path = f.with_suffix(f.suffix + ".meta.json")
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[{topic}] {f.name} -> {meta_path.name}".encode("utf-8", "ignore").decode("utf-8"))
            print(f"    so_hieu={meta['so_hieu']}  hieu_luc_tu={meta['hieu_luc_tu']}".encode("utf-8", "ignore").decode("utf-8"))
            count += 1
    print(f"\nĐã tạo {count} file .meta.json")

if __name__ == "__main__":
    run()