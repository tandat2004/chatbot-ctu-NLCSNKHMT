import subprocess
from pathlib import Path
# pyrefly: ignore [missing-import]
from pypdf import PdfReader
# pyrefly: ignore [missing-import]
import fitz  # PyMuPDF
# pyrefly: ignore [missing-import]
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
RAW_DIR = Path(r"D:\Computer Science\NLCSNKHMT\chatbot-ctu-NLCSNKHMT\Data_CTU_restructured\raw")
OUTPUT_DIR = Path(r"D:\Computer Science\NLCSNKHMT\chatbot-ctu-NLCSNKHMT\Data_CTU_restructured\processed")

# "ocr" = OCR qua ocrmypdf (file scan, không chữ ký số)
# "ocr_signed" = OCR trực tiếp bằng PyMuPDF+tesseract, bỏ qua ocrmypdf (file có chữ ký số)
# "text" = đã có text tốt, trích xuất thẳng bằng pypdf
TARGETS = {
    "hoc_vu/QD3266_Quy_dinh_cong_tac_hoc_vu.pdf": "ocr_signed",
    "hoc_vu/Quy_dinh_dao_tao_truc_tuyen.pdf": "ocr",
    "hoc_phi/QD09_2022_TTg.pdf": "ocr_signed",
    "hoc_phi/QD05_2022_TTg.pdf": "ocr_signed",
    "hoc_phi/Muc_hoc_phi_2026_2027.pdf": "text",
    "hoc_vu/Quy_dinh_mien_cong_nhan_diem.pdf": "ocr",
    "diem_ren_luyen/Quy_che_diem_ren_luyen.pdf": "ocr",
    "hoc_phi/Thong_bao_mien_giam_HK1_2026_2027.pdf": "ocr_signed",
}

def extract_native(pdf_path: Path, out_txt: Path):
    reader = PdfReader(str(pdf_path))
    text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    out_txt.write_text(text, encoding="utf-8")

def extract_ocr(pdf_path: Path, out_txt: Path):
    temp_pdf = out_txt.with_suffix(".temp.pdf")
    cmd = [
        "ocrmypdf",
        "-l", "vie",
        "--sidecar", str(out_txt),
        "--force-ocr",
        str(pdf_path),
        str(temp_pdf),
    ]
    subprocess.run(cmd, check=True)
    if temp_pdf.exists():
        temp_pdf.unlink()

def extract_ocr_signed(pdf_path: Path, out_txt: Path, dpi: int = 300):
    """OCR trực tiếp qua PyMuPDF + pytesseract, không đụng ocrmypdf
    -> dùng cho PDF có chữ ký số mà ocrmypdf từ chối xử lý."""
    doc = fitz.open(str(pdf_path))
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pages_text = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang="vie")
        pages_text.append(text)
    doc.close()
    out_txt.write_text("\n\n".join(pages_text), encoding="utf-8")

def run_pipeline():
    for rel_path, mode in TARGETS.items():
        pdf_file = RAW_DIR / rel_path
        if not pdf_file.exists():
            print(f"Cảnh báo: không tìm thấy {pdf_file}")
            continue

        out_path = (OUTPUT_DIR / rel_path).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[{mode.upper()}] {pdf_file.name} -> {out_path}")
        try:
            if mode == "ocr":
                extract_ocr(pdf_file, out_path)
            elif mode == "ocr_signed":
                extract_ocr_signed(pdf_file, out_path)
            else:
                extract_native(pdf_file, out_path)
            print("  -> xong")
        except Exception as e:
            print(f"  -> LỖI: {e}")

if __name__ == "__main__":
    run_pipeline()

