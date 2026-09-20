# 🇪🇺💬 Chat with the EU AI Act

![Python](https://img.shields.io/badge/python-3.13-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Ollama](https://img.shields.io/badge/ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white)
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=black)
![Streamlit](https://img.shields.io/badge/streamlit-%23FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)
![Qdrant](https://img.shields.io/badge/qdrant-DC244C.svg?style=for-the-badge&logo=qdrant&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/llamaindex-0.14-0ABF53.svg?style=for-the-badge&logo=llamaindex&logoColor=white)
![NVIDIA](https://img.shields.io/badge/nvidia-%2376B900.svg?style=for-the-badge&logo=nvidia&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Ruff](https://img.shields.io/badge/ruff-%23D7FF64.svg?style=for-the-badge&logo=ruff&logoColor=black)
![Pytest](https://img.shields.io/badge/pytest-%230A9EDC.svg?style=for-the-badge&logo=pytest&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Offline](https://img.shields.io/badge/offline-100%25-brightgreen.svg?style=for-the-badge&logo=lock&logoColor=white)
<!-- TODO: replace YOUR_REPO with your GitHub repo name once created, then uncomment:
![CI](https://github.com/stefanicla/YOUR_REPO/actions/workflows/ci/badge.svg)
-->

🤖 Local RAG over the EU AI Act in English. Ask about bans 🚫, high-risk duties ⚖️, GPAI rules 🧠 and fines 💶. Every answer links to the passages it used. Nothing leaves your machine 🔒.

Built with Ollama, Qdrant, LlamaIndex and Streamlit. Docker Compose starts the full stack. `mise` pins Python, `uv` manages deps. Runs on CPU 💻, accelerates on NVIDIA GPUs 🎮.

## ✨ Why the AI Act

The Act is long, structured, and full of cross references. It is a good test for retrieval. A plain chatbot guesses 🎲. This one quotes the article text it found 📖, or says it found nothing 🙅.

## ✅ Prerequisites

* 🐳 Docker + Docker Compose
* 🛠️ `mise` (Python 3.13 and `uv` come from `.mise.toml`)
* 💾 12 GB free disk for models, 8 GB RAM free
* 🎮 No GPU needed. CPU is slower but works. NVIDIA GPU optional for speed (see [GPU setup](#-running-on-gpu-nvidia))

> ⚠️ **Model download size**: The first run pulls two models into the `ollama_data` volume:
> * 🧠 `openbmb/minicpm5-2b` — ~1.6 GB
> * 🔢 `nomic-embed-text` — ~274 MB
> Total: **~1.9 GB** downloaded once, then cached. Ensure you have bandwidth and disk space.

📌 Pinned versions, September 2026: Ollama 0.33.1, Qdrant v1.19.1, LlamaIndex core 0.14.24.

## 🧩 Key components

| Tool | What it does | Why here | Official site |
|---|---|---|---|
| **Ollama** 🤖 | Runs LLMs locally (no API keys, no cloud). Serves `openbmb/minicpm5-2b` for answers and `nomic-embed-text` for embeddings over HTTP. | Keeps everything offline 🔒, zero token cost 💸. | [ollama.com](https://ollama.com/) |
| **Qdrant** 🗄️ | Vector database. Stores 768-dim embeddings, answers cosine-similarity queries in milliseconds with metadata filtering. | Fast ⚡, lightweight, runs in a single container. | [qdrant.tech](https://qdrant.tech/) |
| **Streamlit** 💬 | Python web app framework. Turns a few lines of code into a chat UI with history, expanders for sources, and sidebar controls. | Zero frontend work, built-in chat widgets. | [streamlit.io](https://streamlit.io/) |
| **LlamaIndex** 🔗 | RAG framework. Handles ingestion, chunking, embedding, retrieval, and query synthesis with composable abstractions. | Less boilerplate than wiring it by hand. | [llamaindex.ai](https://www.llamaindex.ai/) |

## 🚀 Quickstart

Two equivalent paths. Pick one.

### Path A — 🛠️ Make (recommended for development)

Uses your local `mise`/`uv` for Python. Faster rebuilds when you change Python code.

```bash
git clone <your-fork> rag-ai-act && cd rag-ai-act
cp .env.example .env
make setup     # starts qdrant+ollama, pulls models, downloads corpus, ingests
make app       # runs Streamlit at http://localhost:8501
```

Open http://localhost:8501 and ask "Which AI practices are prohibited?" 🚫

`make setup` is idempotent — models and vectors live in Docker volumes, so the second run skips downloads and ingest.

### Path B — 🐳 Docker Compose only (no local Python)

Everything runs in containers. Good for a clean machine or CI.

```bash
git clone <your-fork> rag-ai-act && cd rag-ai-act
cp .env.example .env
docker compose up -d --build
docker compose exec app uv run python src/ingest.py --rebuild  # first run only, after models are pulled
```

Open http://localhost:8501 💬. The `ollama-puller` service **auto-pulls the models** defined in `.env` (`LLM_MODEL`, `EMBED_MODEL`). Corpus download + ingest run via `scripts/download_data.sh` and `src/ingest.py` (see Path A bootstrap, or `make docker-ingest`). Subsequent starts are fast because models and vectors are cached in `ollama_data` and `qdrant_data` volumes.

> 📝 **Note**: if you add new documents later, run `docker compose exec app uv run python src/ingest.py --rebuild` (or `make docker-ingest`).

### 🎮 GPU one-liner (NVIDIA machine)

Same project, same code — just add the GPU overlay file. Needs the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Verify with `docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi`.

```bash
cp .env.example .env   # 6GB cards: keep LLM_MODEL=openbmb/minicpm5-2b + LLM_NUM_CTX=4096
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
# or: make up-gpu        (full bootstrap: make setup-gpu)
```

CachyOS/Arch one-time driver setup: `sudo pacman -S nvidia-dkms nvidia-utils nvidia-container-toolkit`, then `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`.

See [Running on GPU](#-running-on-gpu-nvidia) for per-card tuning.

### 🧪 Try it yourself — example queries (both paths)

The corpus covers the full AI Act (prohibited practices 🚫, high-risk rules ⚖️, GPAI duties 🧠, fines 💶, transparency 🔍, Annex III 📎, dates 📅). Paste any of these into the chat:

* 🚫 **Prohibited practices** — *What AI practices are completely prohibited?*
* ⚖️ **High-risk requirements** — *What are the requirements for high-risk AI systems?*
* 🧠 **GPAI providers** — *What must providers of general-purpose AI models do?*
* 💶 **Fines** — *What fines can be imposed under the AI Act?*
* 💬 **Chatbot transparency** — *What transparency obligations exist for chatbots?*
* 📎 **Annex III categories** — *What counts as a high-risk AI system in Annex III?*
* 📅 **Applicability dates** — *When does the AI Act apply?*

The guardrail 🛡️ refuses questions outside the corpus:

* 🙅 **Out of scope** — *Who won the 2024 football world cup?* → the app shows it found nothing relevant and refuses to guess.

Every answer lists the source passages with file, page and similarity score so you can verify ✅.

### 🛑 Stop the stack

| Path | Command | What it does |
|---|---|---|
| A (Make) | `make down` | Stops and removes the three containers. Volumes and models stay. |
| B (Docker) | `docker compose down` | Same — containers removed, volumes kept. |
| 🎮 GPU | `make down-gpu` | Same for the GPU overlay stack. |

To wipe everything including cached models and vectors 🧹:

```bash
docker compose down -v --remove-orphans
```

That deletes the `ollama_data` and `qdrant_data` volumes. Next start will re-pull models and re-ingest.

## ⚙️ Configuration

All settings live in `.env` (copy from `.env.example` — never commit `.env` 🔒). The ones you will change:

| Setting | Default | Notes |
|---|---|---|
| `LLM_MODEL` 🧠 | `openbmb/minicpm5-2b` | Small (2.5B, ~1.6 GB) and fast on CPU. Alternatives: `qwen3:4b`, `qwen3:8b` or `llama3.1:8b`. On 🎮 GPU with 12 GB+ VRAM try `qwen3:8b` |
| `LLM_NUM_CTX` 📏 | `4096` | Caps Ollama context. MiniCPM5 defaults to 4k (safe). Qwen3 defaults to 32k, whose KV cache kills CPU boxes — keep the cap if you switch. Raise to `8192`+ on big-VRAM GPUs |
| `LLM_REQUEST_TIMEOUT` ⏱️ | `300` | Seconds to wait for LLM response. CPU inference can take 60-180s. |
| `EMBED_MODEL` 🔢 | `nomic-embed-text` | 768 dims. Keep the same model for ingest and query ⚠️ |
| `TOP_K` 🎯 | `4` | Passages per answer. 3 to 5 works best |
| `SCORE_THRESHOLD` 🛡️ | `0.40` | Below this the app refuses instead of guessing |
| `COLLECTION` 🗄️ | `ai_act_en` | Qdrant collection name |

## 🏛️ Architecture

Three containers on one local network. No cloud calls ☁️❌.

```
browser -> app (:8501) -> qdrant (:6333) for passages
                       -> ollama (:11434) for embeddings and answers
```

| Piece | Image | Job |
|---|---|---|
| `qdrant` 🗄️ | `qdrant/qdrant:v1.19.1` | Holds 276 vectors, 768 dims, cosine distance, each tagged with source file and page |
| `ollama` 🤖 | `ollama/ollama:0.33.1` | Serves `openbmb/minicpm5-2b` for answers and `nomic-embed-text` for embeddings |
| `app` 💬 | built from `Dockerfile` | Streamlit chat plus retrieval and the refusal guardrail 🛡️ |

Models live in the `ollama_data` volume, vectors in `qdrant_data`. Both survive `docker compose down`, so the second start skips downloads and ingest.

### 📥 Index time

`scripts/download_data.sh` fetches the Act as Markdown from a verbatim mirror, since EUR-Lex challenges automated clients 🤖🚧, then `src/ingest.py` reads the documents, splits them into 512 token chunks with 50 overlap, embeds each chunk through Ollama, and upserts vectors plus metadata into the `ai_act_en` collection. Here 587 KB of Markdown becomes 276 chunks. Ingest runs once. Pass `--rebuild` after new documents arrive.

**Source**: The Markdown is mirrored from the official text 🇪🇺 (Regulation (EU) 2024/1689, OJ L 2024/1689, 12.7.2024) at:
- **Primary (automated)** 🤖: `https://raw.githubusercontent.com/tjf-trojer/eu-ai-act-map/main/corpora/eu/ai-act-2024-1689-en.md` — a clean, verbatim Markdown export used by the download script.
- **Official PDF (manual)** 📄: `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689` — the authentic PDF from EUR-Lex. Download in a browser and place in `data/raw/` if you prefer the PDF source; then re-run ingest.

Reuse of the Act text is permitted under Commission Decision 2011/833/EU with source acknowledgement ✅.

### 🔍 Query time

1. The question is embedded with the same model used at ingest. The name is pinned in `.env` because a different model reads a different vector space ⚠️.
2. Qdrant returns the top 4 passages by cosine similarity 🎯.
3. If the best score sits below 0.40, the app refuses 🙅 and shows what it found. That check stops guessing on questions the corpus cannot answer.
4. Otherwise the passages go into the prompt and `openbmb/minicpm5-2b` answers from them only, at temperature 0 with thinking disabled. Context is capped at 4096 tokens, which covers top-4 retrieval with margin. (If you switch back to Qwen3, keep the cap: it asks for 32k by default and that allocation kills CPU boxes.)
5. The UI lists each passage with source, page and score 📖.

### 📊 Eval

`src/eval.py` replays 12 fixed questions against the retriever and checks the expected keywords land in the top 4. No LLM calls, results in seconds, runs in CI. See the numbers under Eval below.

## 📊 Eval

### What it measures 📏

`src/eval.py` runs a pure-retrieval benchmark against a fixed question set (`data/gold_qa.json`). For each question it asks the retriever for the top 4 passages and checks whether all expected keywords appear in any passage. No LLM calls, no generation cost, runs in seconds — safe for CI ✅.

Two metrics:

* 🎯 **Hit-rate**: share of questions where all keywords are found in the top-K passages.
* 🏆 **MRR (Mean Reciprocal Rank)**: averages the reciprocal rank of the first hit across questions. Higher is better; 1.0 means every answer was at rank 1.

These measure retrieval quality only. They do not judge phrasing, faithfulness or answer relevance — see Roadmap for RAGAS.

### ▶️ Run it

| Path | Command |
|---|---|
| A (Make) | `make eval` |
| B (Docker) | `docker compose exec app uv run python src/eval.py` |

Both require the stack to be running (`make setup` or `docker compose up -d`).

Sample output:

```
Questions: 12  Top-K: 4
Hit-rate: 91.7% (11/12)
MRR: 0.5903
```

Tune chunk size, top K and the model, then rerun. Keep the numbers in your pull requests 📊.

## 🗂️ Project layout

```
docker-compose.yml      qdrant + ollama + app (CPU defaults 💻)
docker-compose.gpu.yml  NVIDIA GPU overlay 🎮 (gpus: all, higher memory/context)
src/ingest.py           docs to vectors 📥
src/app.py              streamlit chat 💬
src/eval.py             keyword hit-rate and MRR 📊
scripts/                bootstrap and download 🛠️
data/raw/               corpus goes here, gitignored 🚫 (see .gitkeep)
data/gold_qa.json       12 seed questions 🧪
.github/workflows/ci.yml  lint + tests ✅
```

## ⚠️ Limits

* 🐢 CPU answers stream at a few tokens per second with 4B, slower with 8B. That is normal without a GPU.
* 📄 PDF extraction is plain text. Tables and footnotes can split oddly.
* 🔑 Keyword eval checks retrieval, not phrasing. It misses good paraphrases.

## 💻 Running on CPU-only machines

The laptop used for development has **no NVIDIA GPU** (Intel integrated graphics only), 33.8 GB RAM (~15 GB free), and 16 cores. Default model is `openbmb/minicpm5-2b` (2.5B, Q4_K_M, ~1.6 GB). To make it run stably:

| Constraint | What we did | Why |
|---|---|---|
| **Context window cap** 📏 | `LLM_NUM_CTX=4096` in `.env`, passed as `num_ctx` via `additional_kwargs` from the LlamaIndex wrapper. | Keeps retrieval + prompt + generation inside 4096 tokens. Top-4 chunks × 512 tokens ≈ 2k, leaving room for the answer. (MiniCPM5 already defaults to 4k — no custom Modelfile needed. Qwen3, by contrast, asks for 32k and needs a `-4k` variant on CPU.) |
| **Thinking disabled** 🧠 | `thinking=False` in the LlamaIndex Ollama wrapper (`src/app.py`). | Thinking models burn CPU tokens on reasoning traces before answering. Disabled, MiniCPM5 answers a RAG query at ~6 tok/s; with thinking on it is ~2x slower and leaks `<think>` traces. |
| **Docker memory limit** 🐳 | `ollama` service limited to 4 GB in `docker-compose.yml`; `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`. | Prevents the host from swapping or the container from being OOM-killed. |
| **Request timeout** ⏱️ | `LLM_REQUEST_TIMEOUT=300` in `.env`; monkey-patched `httpx` and `ollama.Client` defaults in `src/app.py`. | CPU inference for a full answer can take 60–180 seconds; default 30s timeouts would abort. |
| **Model choice** 🧠 | Default `openbmb/minicpm5-2b` (~1.6 GB). Alternatives: `qwen3:4b` (~2.5 GB), `qwen3:8b` or `llama3.1:8b` if you have >12 GB free RAM. | Measured on this CPU (RAG prompt, temp 0, thinking off): MiniCPM5-2B ~5.7 tok/s with a concise grounded answer; `qwen3:4b-4k` ~3.1 tok/s and spent 150 tokens on preamble without answering. Smaller + faster + follows instructions. |
| **Generation speed** 🐢 | ~5–6 tokens/second on this CPU (Intel Core Ultra 7 356H). A 150-token answer takes under a minute. | No GPU acceleration. MiniCPM5-2B is roughly 2x faster than the previous `qwen3:4b` default here. |

## 🎮 Running on GPU (NVIDIA)

The base `docker-compose.yml` is CPU-safe (4 GB cap, 4k context). Adding `-f docker-compose.gpu.yml` (or `make up-gpu`) unlocks the GPU: same three services, same code, higher caps + `gpus: all`. Switching machines = switching the compose command, nothing else.

| Setting | CPU default 💻 | GPU 6 GB VRAM e.g. GTX 1660 Ti 🎮 | GPU 12 GB+ VRAM 🚀 |
|---|---|---|---|
| `LLM_MODEL` 🧠 | `openbmb/minicpm5-2b` | `openbmb/minicpm5-2b` (fits + embed model together) | `qwen3:8b` or `llama3.1:8b` |
| `LLM_NUM_CTX` 📏 | `4096` | `4096` (`8192` max, 2B/4B models only) | `8192` or `16384` |
| Compose file 🐳 | `docker-compose.yml` | add `-f docker-compose.gpu.yml` (or `make up-gpu`) | same overlay |
| Memory cap 💾 | 4 GB | 12 GB (preset in overlay) | raise in overlay to 16–24 GB |

> ⚠️ Keep `EMBED_MODEL=nomic-embed-text` unless you rebuild the Qdrant collection — embeddings from different models live in different vector spaces and are not interchangeable. If you switch it, run ingest with `--rebuild`.
>
> ⚠️ 6 GB VRAM note: `qwen3:8b` (~5–6 GB weights) + embeddings + KV cache does **not** comfortably fit — expect partial CPU offload (slower) or OOM. If Ollama logs out-of-memory, set `OLLAMA_MAX_LOADED_MODELS=1` / `LLM_NUM_CTX=2048` in the overlay, or stay on `openbmb/minicpm5-2b`, which is the recommended 6 GB setup and still much faster on GPU than on CPU.

## 🗺️ Roadmap

* 🔀 Hybrid dense plus BM25 search and a reranker
* 📑 Better PDF parsing for tables
* 🧪 RAGAS scoring for faithfulness and answer relevance
* 🎮 CUDA-verified compose profile + larger-model eval numbers

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and pull requests welcome 🙏. Please include eval numbers (`make eval`) in RAG-related PRs 📊.

## 🔒 Security

See [SECURITY.md](SECURITY.md). No API keys or cloud credentials are used by design 🔑❌. Do not commit `.env` or model files. Report vulnerabilities privately — see the policy.

## 📜 Licence

MIT. See [LICENSE](LICENSE). The AI Act text itself belongs to the EU 🇪🇺 and stays outside this repo (downloaded at setup, gitignored). Reuse is permitted under Commission Decision 2011/833/EU with source acknowledgement ✅.
