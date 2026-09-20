.PHONY: setup setup-gpu up up-gpu down down-gpu logs logs-gpu pull-models ingest ingest-rebuild app eval lint test clean docker-ingest

setup:
	cp -n .env.example .env || true
	docker compose up -d qdrant ollama
	./scripts/bootstrap.sh

# Full bootstrap on the NVIDIA machine (same steps, GPU overlay enabled).
setup-gpu:
	cp -n .env.example .env || true
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d qdrant ollama
	./scripts/bootstrap.sh

up:
	docker compose up -d qdrant ollama app

down:
	docker compose down

logs:
	docker compose logs -f

pull-models:
	ollama pull nomic-embed-text
	ollama pull openbmb/minicpm5-2b

ingest:
	uv run python src/ingest.py

ingest-rebuild:
	uv run python src/ingest.py --rebuild

app:
	uv run streamlit run src/app.py --server.port=8501

eval:
	uv run python src/eval.py

lint:
	uv run ruff check src tests

test:
	uv run pytest -q

clean:
	docker compose down -v --remove-orphans || true
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__

# NVIDIA GPU machine (needs NVIDIA Container Toolkit + docker-compose.gpu.yml).
# 6GB cards (e.g. GTX 1660 Ti Mobile): keep LLM_MODEL=openbmb/minicpm5-2b, LLM_NUM_CTX=4096.
# Bigger VRAM (>=12GB): LLM_MODEL=qwen3:8b LLM_NUM_CTX=8192 make up-gpu
up-gpu:
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build

down-gpu:
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml down

logs-gpu:
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml logs -f

# One-shot ingest inside the app container (for pure-Docker setups).
docker-ingest:
	docker compose exec app uv run python src/ingest.py --rebuild
