"""Shared settings for the RAG service. English UK comments throughout."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_str(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value if value else default


def get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


OLLAMA_BASE_URL = get_str("OLLAMA_BASE_URL", "http://localhost:11434")
QDRANT_URL = get_str("QDRANT_URL", "http://localhost:6333")

LLM_MODEL = get_str("LLM_MODEL", "openbmb/minicpm5-2b")
EMBED_MODEL = get_str("EMBED_MODEL", "nomic-embed-text")

COLLECTION = get_str("COLLECTION", "ai_act_en")
DATA_DIR = get_str("DATA_DIR", "data/raw")

CHUNK_SIZE = get_int("CHUNK_SIZE", 512)
CHUNK_OVERLAP = get_int("CHUNK_OVERLAP", 50)
TOP_K = get_int("TOP_K", 4)
SCORE_THRESHOLD = get_float("SCORE_THRESHOLD", 0.40)
# Cap for Ollama num_ctx. Qwen3 reports a 32k native window, whose KV cache
# OOM-kills llama-server on CPU boxes. 4096 covers top-4 retrieval with margin.
LLM_NUM_CTX = get_int("LLM_NUM_CTX", 4096)
# LLM request timeout in seconds. CPU inference can take 60-180s for longer answers.
LLM_REQUEST_TIMEOUT = get_float("LLM_REQUEST_TIMEOUT", 300.0)
