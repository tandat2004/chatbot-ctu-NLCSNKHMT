import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
try:
    from generate import KnowledgeBase, Answerer
except ModuleNotFoundError:
    from rag_pipeline.generate import KnowledgeBase, Answerer

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi UnicodeEncodeError
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

# Khởi tạo FastAPI
app = FastAPI(title="CTU Chatbot API")

# Cho phép Frontend gọi API mà không bị chặn lỗi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException
import urllib.parse
import unicodedata

# Cung cấp file tĩnh (HTML, CSS, JS) để người dùng có thể mở thẳng http://127.0.0.1:8000
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = ROOT_DIR / "data_pipeline" / "data" / "1_raw"

if (ROOT_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(ROOT_DIR / "css")), name="css")
if (ROOT_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(ROOT_DIR / "js")), name="js")

@app.get("/")
async def serve_homepage():
    index_file = ROOT_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"status": "ok", "message": "CTU Chatbot API is running"}

@app.get("/download/{filename:path}")
async def download_document(filename: str):
    """Tải tài liệu gốc (PDF, DOCX, XLSX...) từ data_pipeline/data/1_raw"""
    decoded_name = urllib.parse.unquote(filename).strip()
    
    def norm(s: str) -> str:
        return unicodedata.normalize('NFC', s.lower())

    norm_target = norm(decoded_name)
    
    # 1. Kiểm tra trực tiếp file path
    direct = DATA_RAW_DIR / decoded_name
    if direct.is_file():
        media_type = "application/pdf" if direct.name.lower().endswith(".pdf") else "application/octet-stream"
        return FileResponse(
            str(direct),
            filename=direct.name,
            media_type=media_type
        )
        
    # 2. Duyệt tìm trong DATA_RAW_DIR với chuẩn hóa Unicode NFC
    if DATA_RAW_DIR.exists():
        # Khớp chính xác tên đã chuẩn hóa
        for f in DATA_RAW_DIR.iterdir():
            if f.is_file() and norm(f.name) == norm_target:
                media_type = "application/pdf" if f.name.lower().endswith(".pdf") else "application/octet-stream"
                return FileResponse(
                    str(f),
                    filename=f.name,
                    media_type=media_type
                )
        # Khớp theo stem hoặc tên tương đồng
        stem_target = Path(decoded_name).stem.lower()
        if len(stem_target) >= 4:
            for f in DATA_RAW_DIR.iterdir():
                if f.is_file() and (stem_target in norm(f.name) or norm(Path(f.name).stem) == stem_target):
                    media_type = "application/pdf" if f.name.lower().endswith(".pdf") else "application/octet-stream"
                    return FileResponse(
                        str(f),
                        filename=f.name,
                        media_type=media_type
                    )

    raise HTTPException(status_code=404, detail=f"Không tìm thấy tài liệu '{decoded_name}' trên máy chủ.")

@app.get("/api/documents")
async def list_documents():
    """Danh sách tất cả tài liệu có sẵn để người dùng tra cứu và tải về"""
    docs = []
    if DATA_RAW_DIR.exists():
        for f in sorted(DATA_RAW_DIR.iterdir(), key=lambda x: x.name):
            if f.is_file():
                ext = f.suffix.lstrip(".").upper()
                size_kb = round(f.stat().st_size / 1024, 1)
                docs.append({
                    "name": f.name,
                    "type": ext,
                    "size_kb": size_kb,
                    "download_url": f"/download/{urllib.parse.quote(f.name)}"
                })
    return {"total": len(docs), "documents": docs}

# Tải cơ sở dữ liệu và AI vào RAM (chỉ chạy 1 lần khi bật server)
print("Đang khởi động hệ thống AI...")
kb = KnowledgeBase()
# Đặt mặc định là Groq để phản hồi nhanh nhất (bạn có thể đổi sang gemini)
# Dùng model Llama 3 siêu nhanh:
bot = Answerer(kb, provider="groq", model="openai/gpt-oss-20b", temperature=0.2)
print("Hệ thống đã sẵn sàng!")

# Định nghĩa dữ liệu đầu vào
class ChatRequest(BaseModel):
    query: str

# Hàm phân loại chủ đề (Yêu cầu 4)
def classify_topic(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["học phí", "tiền", "học bổng", "miễn giảm"]):
        return "💰 Tài chính & Học bổng"
    elif any(w in q for w in ["ký túc xá", "ktx", "nội trú", "phòng", "chỗ ở"]):
        return "🏠 Ký túc xá & Đời sống"
    elif any(w in q for w in ["đăng ký", "tín chỉ", "điểm", "thi", "nghỉ học", "bảo lưu", "phòng học", "c1", "c2"]):
        return "📚 Đào tạo & Học vụ"
    return "🔍 Thông tin chung"

# API Endpoint xử lý chat
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    topic = classify_topic(req.query)
    result = bot.answer(req.query)
    
    # Xử lý nguồn chi tiết (lọc trùng lặp, lấy metadata và trích đoạn phục vụ UI)
    sources = []
    seen = set()
    for h in result.hits:
        raw_src = h.metadata.get('source_file', '')
        clean_src = raw_src.split(';')[0].strip() if raw_src else "Không rõ"
        if clean_src and clean_src != "Không rõ" and clean_src not in seen:
            seen.add(clean_src)
            title = h.metadata.get('title') or clean_src
            page = str(h.metadata.get('page') or '').strip()
            section = str(h.metadata.get('section') or '').strip()
            excerpt = h.text.strip()
            if len(excerpt) > 500:
                excerpt = excerpt[:500] + "..."
            sources.append({
                "file": clean_src,
                "title": title,
                "section": section,
                "page": page if page != "None" and page != "nan" else "",
                "excerpt": excerpt,
                "download_url": f"/download/{urllib.parse.quote(clean_src)}"
            })
            
    return {
        "text": result.text,
        "topic": topic,
        "sources": sources
    }

if __name__ == "__main__":
    # Khởi chạy server ở cổng 8000 (app_dir giúp tìm đúng module api.py dù đứng ở bất kỳ thư mục nào)
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(Path(__file__).resolve().parent))