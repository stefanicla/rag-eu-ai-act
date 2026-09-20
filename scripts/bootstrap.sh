#!/usr/bin/env bash
# One-click bootstrap for a clean machine with Docker + mise.
# Steps: services up, wait, pull Ollama models, fetch PDF, ingest.
set -euo pipefail

: "${LLM_MODEL:=openbmb/minicpm5-2b}"
: "${EMBED_MODEL:=nomic-embed-text}"

echo "Starting qdrant + ollama..."
docker compose up -d qdrant ollama

echo "Waiting for Qdrant on :6333..."
for _ in $(seq 1 30); do
  if curl -fsS http://localhost:6333/readyz >/dev/null 2>&1; then break; fi
  sleep 2
done

echo "Waiting for Ollama on :11434..."
for _ in $(seq 1 30); do
  if curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then break; fi
  sleep 2
done

echo "Pulling models: ${EMBED_MODEL}, ${LLM_MODEL}..."
docker exec rag-ollama ollama pull "${EMBED_MODEL}"
docker exec rag-ollama ollama pull "${LLM_MODEL}"

./scripts/download_data.sh

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Ingesting PDFs into Qdrant..."
uv run python src/ingest.py --rebuild

echo "Bootstrap complete."
echo "Run the chat:  uv run streamlit run src/app.py"
echo "Or with Docker: docker compose up -d app  (http://localhost:8501)"
