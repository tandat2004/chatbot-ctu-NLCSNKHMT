"""Cấu hình trung tâm cho pipeline RAG. Có thể ghi đè bằng biến môi trường."""
import os
from pathlib import Path

# Thư mục dữ liệu (chứa raw/, processed/, faq/)
_project_root = Path(__file__).resolve().parent.parent
_candidate_data = _project_root / "Data_CTU_restructured"
_default_data = _candidate_data if _candidate_data.exists() else Path("Data_CTU_restructured").resolve()
DATA_DIR = Path(os.getenv("CTU_DATA_DIR", str(_default_data))).resolve()

# Nơi lưu vector database (ChromaDB dạng file, không cần server)
_default_vector = Path(__file__).resolve().parent / "vector_store"
VECTOR_DIR = Path(os.getenv("CTU_VECTOR_DIR", str(_default_vector))).resolve()
COLLECTION_NAME = "ctu_student_assistant"

# Mô hình embedding. Lựa chọn thay thế nhẹ hơn: "intfloat/multilingual-e5-base"
# ("dummy" chỉ dùng để kiểm thử pipeline khi không tải được model).
EMBEDDING_MODEL = os.getenv("CTU_EMBED_MODEL", "BAAI/bge-m3")
MAX_SEQ_LENGTH = 512

# Chia đoạn (đơn vị: từ/âm tiết, tiếng Việt ~1.3-1.6 token/âm tiết với bge-m3)
# 280 từ ≈ 400-450 token, nằm gọn trong giới hạn 512 của model.
CHUNK_MAX_WORDS = 280
CHUNK_MIN_WORDS = 40      # section nhỏ hơn mức này sẽ được gộp với section kế
CHUNK_OVERLAP_WORDS = 40  # chồng lấn tối đa giữa 2 chunk liên tiếp trong 1 section

# Tìm kiếm
DEFAULT_TOP_K = 5
RRF_K = 60                # hằng số của Reciprocal Rank Fusion
FAQ_BOOST = 1.10          # nhân điểm cho chunk FAQ (đã được soạn sẵn, chuẩn hóa)
LOW_CONFIDENCE_SIM = 0.35 # cosine thấp hơn mức này => coi là "không chắc"; cần tinh chỉnh

# Tên chủ đề của FAQ lấy từ tên file (faq_hoc_phi.md -> "hoc_phi"). Nếu tên file không khớp
# tên thư mục trong processed/, khai báo ánh xạ ở đây (khóa viết THƯỜNG, bỏ tiền tố "faq").
FAQ_TOPIC_ALIASES = {
    "phong-ctsv-ctu": "hoc_bong_ctsv",   # faq/FAQ-Phong-CTSV-CTU.md  (hãy xác nhận cho đúng)
}

# Sinh câu trả lời (bước 3)
GEMINI_MODEL = os.getenv("CTU_GEMINI_MODEL", "gemini-3.6-flash")
OPENAI_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = float(os.getenv("CTU_LLM_TEMPERATURE", "0.2"))
