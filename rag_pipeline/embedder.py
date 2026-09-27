"""Bao bọc mô hình embedding. Mặc định: BAAI/bge-m3 (đa ngôn ngữ, mạnh tiếng Việt)."""
from __future__ import annotations

import hashlib
import math
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import MAX_SEQ_LENGTH
from textutil import tokenize


class STEmbedder:
    """Embedding bằng sentence-transformers (bge-m3, multilingual-e5, ...)."""

    def __init__(self, model_name: str, max_seq_length: int = MAX_SEQ_LENGTH):
        from sentence_transformers import SentenceTransformer
        import torch

        if torch.cuda.is_available():
            device = "cuda"
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
        print(f"[embedder] Nạp {model_name} trên {device} (lần đầu sẽ tải ~2GB với bge-m3)...")
        self.model = SentenceTransformer(model_name, device=device)
        self.model.max_seq_length = max_seq_length
        # Họ E5 bắt buộc có tiền tố; bge-m3 thì không.
        if "e5" in model_name.lower():
            self.q_prefix, self.p_prefix = "query: ", "passage: "
        else:
            self.q_prefix = self.p_prefix = ""

    def embed_passages(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        return self.model.encode(
            [self.p_prefix + t for t in texts],
            batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True,
        ).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([self.q_prefix + text], normalize_embeddings=True)[0].tolist()


class HashEmbedder:
    """Embedding băm từ (feature hashing) — KHÔNG có ngữ nghĩa thật.

    Chỉ dùng để kiểm thử luồng pipeline offline (CTU_EMBED_MODEL=dummy).
    """

    dim = 768

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        for t in tokenize(text):
            h = int(hashlib.md5(t.encode()).hexdigest(), 16)
            v[h % self.dim] += 1.0 if (h >> 64) & 1 else -1.0
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]

    def embed_passages(self, texts, batch_size: int = 16):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


def get_embedder(model_name: str):
    if model_name == "dummy":
        print("[embedder] CẢNH BÁO: đang dùng 'dummy' — chỉ để kiểm thử, không có ngữ nghĩa thật.")
        return HashEmbedder()
    return STEmbedder(model_name)
