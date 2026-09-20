# 🤝 Contributing

Thanks for stopping by! This is a small, local-first RAG project — issues and PRs are welcome 🙏.

## Quick start 🛠️

```bash
cp .env.example .env
make setup     # qdrant + ollama, models, corpus, ingest
make app       # http://localhost:8501
```

Pure-Docker alternative: `docker compose up -d --build`, then `make docker-ingest` once.

GPU machine: `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build` (see README 🎮).

## What to include in a PR 📦

- ✅ `make lint` (ruff) and `make test` (pytest) pass.
- 📊 For retrieval/RAG changes: paste `make eval` output (hit-rate + MRR) before/after.
- 📝 Update README/docs when you change setup, config keys, or behaviour.
- 🧹 Keep diffs small; one concern per PR.

## Style 🎨

- Python 3.13, `ruff` line-length 100.
- English (UK) comments in `src/` where it matters.
- No secrets in code or fixtures — `.env` stays local 🔒.

## Reporting bugs 🐛

Use the issue template: what you ran, what you expected, what happened, plus `docker compose ps`, relevant logs (`make logs`), OS (CPU/GPU, RAM/VRAM), and model names.

## Licence 📜

By contributing you agree your changes are released under the repo's [MIT Licence](LICENSE).
