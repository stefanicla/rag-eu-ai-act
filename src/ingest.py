"""Ingest documents from data/raw into Qdrant. Run once, rerun on new documents."""

from __future__ import annotations

import argparse
from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import settings


def read_pdf(path: Path) -> list[tuple[int, str]]:
    """Return a list of (page_number, text) pairs. Skips empty pages."""
    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((i, text))
    return pages


def read_text_file(path: Path) -> str:
    """Read a plain text or Markdown file."""
    return path.read_text(encoding="utf-8").strip()


def build_nodes(data_dir: Path) -> list[TextNode]:
    splitter = SentenceSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    nodes: list[TextNode] = []
    pdfs = sorted(data_dir.glob("*.pdf")) + sorted(data_dir.glob("*.PDF"))
    texts = sorted(data_dir.glob("*.md")) + sorted(data_dir.glob("*.txt"))
    if not pdfs and not texts:
        raise SystemExit(f"No documents found in {data_dir}. Run scripts/download_data.sh first.")
    for pdf in pdfs:
        for page_no, text in read_pdf(pdf):
            for chunk in splitter.split_text(text):
                chunk = chunk.strip()
                if chunk:
                    nodes.append(
                        TextNode(
                            text=chunk,
                            metadata={"source": pdf.name, "page": page_no},
                        )
                    )
    for doc in texts:
        text = read_text_file(doc)
        if not text:
            continue
        for chunk in splitter.split_text(text):
            chunk = chunk.strip()
            if chunk:
                nodes.append(
                    TextNode(text=chunk, metadata={"source": doc.name, "page": 0})
                )
    return nodes


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into Qdrant.")
    parser.add_argument("--rebuild", action="store_true", help="Drop the collection first.")
    args = parser.parse_args()

    data_dir = Path(settings.DATA_DIR)
    nodes = build_nodes(data_dir)
    print(f"Prepared {len(nodes)} chunks from {data_dir}.")

    embed_model = OllamaEmbedding(
        model_name=settings.EMBED_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
    probe_dim = len(embed_model.get_text_embedding("dimension probe"))
    print(f"Embedding model: {settings.EMBED_MODEL} ({probe_dim} dims).")

    client = QdrantClient(url=settings.QDRANT_URL)
    if args.rebuild and client.collection_exists(settings.COLLECTION):
        client.delete_collection(settings.COLLECTION)
        print(f"Deleted collection {settings.COLLECTION}.")

    if not client.collection_exists(settings.COLLECTION):
        client.create_collection(
            collection_name=settings.COLLECTION,
            vectors_config=VectorParams(size=probe_dim, distance=Distance.COSINE),
        )
        print(f"Created collection {settings.COLLECTION}.")

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.COLLECTION,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    count = client.count(settings.COLLECTION, exact=True).count
    print(f"Done. Collection {settings.COLLECTION} now holds {count} points.")


if __name__ == "__main__":
    main()
