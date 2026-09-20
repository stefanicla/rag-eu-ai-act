"""Streamlit chat over the EU AI Act. Shows sources for every answer."""

from __future__ import annotations

import httpx
import streamlit as st
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

import settings


# Patch httpx default timeout globally so Ollama's internal client inherits it
_orig_client_init = httpx.Client.__init__

def _patched_client_init(self, *args, **kwargs):
    kwargs.setdefault("timeout", httpx.Timeout(settings.LLM_REQUEST_TIMEOUT, connect=10.0))
    return _orig_client_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init

# Also patch ollama.Client to pass timeout via kwargs to internal httpx client
import ollama
_orig_ollama_init = ollama.Client.__init__

def _patched_ollama_init(self, host=None, **kwargs):
    # The ollama Client passes **kwargs to its internal httpx.Client
    kwargs.setdefault("timeout", httpx.Timeout(settings.LLM_REQUEST_TIMEOUT, connect=10.0))
    return _orig_ollama_init(self, host, **kwargs)

ollama.Client.__init__ = _patched_ollama_init


@st.cache_resource(show_spinner="Connecting to Qdrant and Ollama...")
def load_index() -> VectorStoreIndex:
    embed_model = OllamaEmbedding(
        model_name=settings.EMBED_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
    client = QdrantClient(url=settings.QDRANT_URL)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.COLLECTION,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )


def answer(question: str, top_k: int, threshold: float) -> dict:
    index = load_index()
    llm = Ollama(
        model=settings.LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.0,
        context_window=settings.LLM_NUM_CTX,
        request_timeout=settings.LLM_REQUEST_TIMEOUT,
        additional_kwargs={"num_ctx": settings.LLM_NUM_CTX},
        keep_alive="24h",
        # MiniCPM5 and Qwen3 are thinking models. Thinking is off for RAG:
        # it doubles latency on CPU and leaks reasoning traces into answers.
        thinking=False,
    )
    retriever = index.as_retriever(similarity_top_k=top_k)
    hits = retriever.retrieve(question)
    if not hits:
        return {"text": "I found nothing relevant in the indexed documents.", "hits": []}
    best = max((h.score or 0.0) for h in hits)
    if best < threshold:
        return {
            "text": (
                "I cannot answer from the indexed documents. "
                f"Best match scored {best:.2f}, below the {threshold:.2f} limit. "
                "Try rephrasing or lower the threshold in the sidebar."
            ),
            "hits": hits,
        }
    engine = index.as_query_engine(llm=llm, similarity_top_k=top_k)
    response = engine.query(question)
    return {"text": str(response), "hits": hits}


st.set_page_config(page_title="AI Act RAG", page_icon="📘", layout="wide")
st.title("Chat with the EU AI Act")
st.caption(f"Local RAG. Model {settings.LLM_MODEL}. Embeddings {settings.EMBED_MODEL}. No cloud calls.")

with st.sidebar:
    st.header("Retrieval")
    top_k = st.slider("Top K passages", 1, 8, settings.TOP_K)
    threshold = st.slider("Refuse below score", 0.0, 1.0, settings.SCORE_THRESHOLD, 0.05)
    st.divider()
    st.write(f"Collection: `{settings.COLLECTION}`")
    try:
        client = QdrantClient(url=settings.QDRANT_URL)
        n = client.count(settings.COLLECTION, exact=True).count
        st.write(f"Indexed points: **{n}**")
    except Exception as exc:  # noqa: BLE001 - show connection issues in UI
        st.warning(f"Qdrant not reachable: {exc}")

if "history" not in st.session_state:
    st.session_state.history = []

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

question = st.chat_input("Ask about risk categories, bans, fines, GPAI duties...")
if question:
    st.session_state.history.append(("user", question))
    st.chat_message("user").write(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching the indexed text..."):
            result = answer(question, top_k, threshold)
        st.write(result["text"])
        if result["hits"]:
            with st.expander(f"Sources ({len(result['hits'])})"):
                for i, h in enumerate(result["hits"], 1):
                    meta = h.node.metadata or {}
                    score = h.score or 0.0
                    st.markdown(f"**[{i}] {meta.get('source', 'unknown')} p.{meta.get('page', '?')} (score {score:.3f})**")
                    st.caption(h.node.text[:900])
    st.session_state.history.append(("assistant", result["text"]))
