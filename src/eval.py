"""Keyword eval for retrieval. No LLM calls, safe for CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

import settings


def load_retriever(top_k: int) -> VectorIndexRetriever:
    embed_model = OllamaEmbedding(
        model_name=settings.EMBED_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
    client = QdrantClient(url=settings.QDRANT_URL)
    vector_store = QdrantVectorStore(client=client, collection_name=settings.COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    return VectorIndexRetriever(index=index, similarity_top_k=top_k)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval with keyword hits.")
    parser.add_argument("--qa", default="data/gold_qa.json")
    parser.add_argument("--min-hit-rate", type=float, default=0.0)
    parser.add_argument("--top-k", type=int, default=0)
    args = parser.parse_args()

    top_k = args.top_k or settings.TOP_K
    items = json.loads(Path(args.qa).read_text(encoding="utf-8"))
    retriever = load_retriever(top_k)

    hits = 0
    ranks: list[float] = []
    for item in items:
        nodes = retriever.retrieve(item["question"])
        keywords = [k.lower() for k in item["expected_keywords"]]
        rank = None
        for i, node in enumerate(nodes, 1):
            text = node.text.lower()
            if all(k in text for k in keywords):
                rank = i
                break
        ok = rank is not None
        hits += int(ok)
        ranks.append(1.0 / rank if rank else 0.0)
        print(f"[{'HIT' if ok else 'MISS'} rank={rank}] {item['id']}: {item['question'][:70]}")

    hit_rate = hits / len(items) if items else 0.0
    mrr = sum(ranks) / len(ranks) if ranks else 0.0
    print("=" * 52)
    print(f"Questions: {len(items)}  Top-K: {top_k}")
    print(f"Hit-rate: {hit_rate:.1%} ({hits}/{len(items)})")
    print(f"MRR: {mrr:.4f}")
    print("=" * 52)
    if hit_rate < args.min_hit_rate:
        raise SystemExit(f"Hit-rate {hit_rate:.1%} below minimum {args.min_hit_rate:.1%}.")


if __name__ == "__main__":
    main()
