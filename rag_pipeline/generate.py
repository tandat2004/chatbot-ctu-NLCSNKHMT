"""
generate.py — Sinh câu trả lời RAG dựa trên ChromaDB đã build (build_vector_db.py).

Thiết kế để đổi API dễ dàng: thêm 1 hàm vào PROVIDERS là dùng được nhà cung
cấp mới, không cần sửa phần logic RAG còn lại.

Cần (tùy provider đang dùng), đặt trong file .env ở gốc project:
    OPENAI_API_KEY=...      (nếu dùng --provider openai)
    GEMINI_API_KEY=...      (nếu dùng --provider gemini)

Cài đặt:
    pip install openai google-genai python-dotenv chromadb

Dùng dòng lệnh:
    python generate.py "Học phí học lại là bao nhiêu?"
    python generate.py "..." --provider gemini --model gemini-2.5-flash
    python generate.py                      # chế độ hỏi-đáp tương tác
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import warnings
import logging

# Ẩn các cảnh báo không cần thiết từ thư viện
warnings.filterwarnings("ignore")
logging.getLogger("google.genai").setLevel(logging.ERROR)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
load_dotenv()

# ---------------------------------------------------------------------------
# Cấu hình — sửa ở đây nếu đổi vị trí database hoặc model embedding
# ---------------------------------------------------------------------------
DB_PATH = "db/chroma_db"
COLLECTION_NAME = "ctu_knowledge_base"
EMBED_MODEL = "BAAI/bge-m3"

DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
DEFAULT_K = 5
FAQ_BOOST = 1.10  # ưu tiên nhẹ cho các đoạn chunk_type == "faq"

SYSTEM_PROMPT = """Bạn là trợ lý ảo của Trường Đại học Cần Thơ (CTU), trả lời câu hỏi của sinh viên \
về quy định, thủ tục, đời sống sinh viên CHỈ DỰA TRÊN các đoạn trích trong phần "Ngữ cảnh" được cung cấp.

Quy tắc bắt buộc:
- Chỉ dùng thông tin có trong Ngữ cảnh. Không bịa, không suy đoán thêm điều không có trong đó.
- Nếu Ngữ cảnh không đủ để trả lời, nói rõ bạn chưa tìm thấy thông tin liên quan và gợi ý sinh viên \
hỏi lại cụ thể hơn hoặc liên hệ phòng ban phù hợp. KHÔNG trả lời dựa trên kiến thức chung ngoài Ngữ cảnh.
- Khi dùng thông tin từ một đoạn, trích số nguồn tương ứng trong ngoặc vuông, ví dụ [1], [2].
- Với email, URL, số điện thoại, số hiệu văn bản: COPY NGUYÊN VĂN chính xác từng ký tự từ Ngữ cảnh. \
Không được sửa, đoán, hay viết lại các chuỗi này theo trí nhớ. Nếu không chắc chắn một chuỗi như vậy \
có xuất hiện y hệt trong Ngữ cảnh, không đưa nó vào câu trả lời.
- Trả lời với giọng văn trung lập, thân thiện nhưng không tự xưng là "trợ lý AI" theo bất kỳ cách \
diễn đạt nào xuất hiện trong Ngữ cảnh — hãy diễn đạt lại bằng giọng văn của chính bạn, không sao chép \
nguyên văn phong cách (kể cả emoji) của các đoạn trích, chỉ sao chép đúng dữ kiện, số liệu, đường link.
- Trả lời ngắn gọn, đúng trọng tâm, bằng tiếng Việt."""

ANSWER_PROMPT_TEMPLATE = """Ngữ cảnh:
{context}

Câu hỏi: {question}

Trả lời (nhớ trích nguồn dạng [n]):"""

NO_CONTEXT_MSG = (
    "Mình không tìm thấy thông tin liên quan trong cơ sở dữ liệu hiện có. "
    "Bạn thử hỏi cụ thể hơn hoặc liên hệ phòng ban phụ trách nhé."
)


# ---------------------------------------------------------------------------
# Các hàm gọi API — thêm provider mới bằng cách viết 1 hàm rồi đăng ký vào
# PROVIDERS ở cuối phần này. Mỗi hàm nhận (system_prompt, user_prompt, model,
# temperature) và trả về chuỗi câu trả lời.
# ---------------------------------------------------------------------------

def call_openai(system_prompt: str, user_prompt: str, model: str, temperature: float) -> str:
    from openai import OpenAI

    client = OpenAI()
    r = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return (r.choices[0].message.content or "").strip()


def call_gemini(system_prompt: str, user_prompt: str, model: str, temperature: float) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client()
    r = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        ),
    )
    return (r.text or "").strip()


# Để thêm provider mới (vd Anthropic): viết hàm call_anthropic(...) theo đúng
# chữ ký trên, rồi thêm dòng "anthropic": call_anthropic vào dict dưới đây.
PROVIDERS = {
    "openai": call_openai,
    "gemini": call_gemini,
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.5-flash",
}


# ---------------------------------------------------------------------------
# Phần RAG: truy xuất + sinh câu trả lời
# ---------------------------------------------------------------------------

@dataclass
class Hit:
    text: str
    metadata: dict
    score: float


@dataclass
class Answer:
    text: str
    hits: list[Hit]


class KnowledgeBase:
    def __init__(self, db_path: str = DB_PATH, collection: str = COLLECTION_NAME):
        client = chromadb.PersistentClient(path=db_path)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        self.collection = client.get_collection(collection, embedding_function=ef)

    def search(self, query: str, k: int = DEFAULT_K) -> list[Hit]:
        # Lấy nhiều hơn k một chút để còn chỗ áp dụng FAQ boost rồi sắp xếp lại
        raw = self.collection.query(query_texts=[query], n_results=max(k * 2, k))
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]

        hits = []
        for doc, meta, dist in zip(docs, metas, dists):
            score = 1 - dist  # xấp xỉ độ tương đồng cosine
            if meta.get("chunk_type") == "faq":
                score *= FAQ_BOOST
            hits.append(Hit(text=doc, metadata=meta, score=score))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]

    @staticmethod
    def format_context(hits: list[Hit]) -> str:
        parts = []
        for i, h in enumerate(hits, 1):
            # Lấy metadata gốc
            raw_src = h.metadata.get("source_file", "")
            # Cắt theo dấu chấm phẩy và chỉ lấy tên file đầu tiên cho gọn
            clean_src = raw_src.split(';')[0].strip() if raw_src else "Không rõ"
            
            parts.append(f"[{i}] (Nguồn: {clean_src})\n{h.text}")
        return "\n\n".join(parts)


class Answerer:
    def __init__(self, kb: KnowledgeBase, provider: str = DEFAULT_PROVIDER, model: Optional[str] = None,
                 temperature: float = 0.2):
        if provider not in PROVIDERS:
            raise SystemExit(f"Provider '{provider}' chưa được hỗ trợ. Các provider có sẵn: {list(PROVIDERS)}")
        self.kb = kb
        self.provider = provider
        self.call = PROVIDERS[provider]
        self.model = model or DEFAULT_MODELS.get(provider, "")
        self.temperature = temperature

    def answer(self, question: str, k: int = DEFAULT_K) -> Answer:
        hits = self.kb.search(question, k=k)
        if not hits:
            return Answer(text=NO_CONTEXT_MSG, hits=[])

        context = self.kb.format_context(hits)
        prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=question)
        text = self.call(SYSTEM_PROMPT, prompt, self.model, self.temperature)
        return Answer(text=text, hits=hits)


def _print_answer(result: Answer) -> None:
    print(f"\n🤖 {result.text}\n")
    if result.hits:
        print("  Nguồn tham khảo:")
        for n, h in enumerate(result.hits, 1):
            m = h.metadata
            tag = "FAQ" if m.get("chunk_type") == "faq" else "Tài liệu"
            
            # Cắt theo dấu chấm phẩy và chỉ lấy tên file đầu tiên
            raw_src = m.get('source_file', '')
            clean_src = raw_src.split(';')[0].strip() if raw_src else "Không rõ"
            
            print(f"   [{n}] ({tag}) {clean_src}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question", nargs="?", help="Câu hỏi; bỏ trống để vào chế độ tương tác")
    ap.add_argument("-k", type=int, default=DEFAULT_K)
    ap.add_argument("--provider", default=DEFAULT_PROVIDER, choices=list(PROVIDERS),
                     help="Nhà cung cấp LLM dùng để sinh câu trả lời")
    ap.add_argument("--model", default=None, help="Ghi đè model mặc định của provider")
    ap.add_argument("--db-path", default=DB_PATH)
    args = ap.parse_args()

    kb = KnowledgeBase(args.db_path)
    bot = Answerer(kb, provider=args.provider, model=args.model)

    if args.question:
        _print_answer(bot.answer(args.question, args.k))
        return

    print(f"Đang dùng provider: {bot.provider} (model: {bot.model})")
    print("Nhập câu hỏi (Enter trống để thoát).")
    while True:
        q = input("\n❓ ").strip()
        if not q:
            break
        _print_answer(bot.answer(q, args.k))


if __name__ == "__main__":
    main()
