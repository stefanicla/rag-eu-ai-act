# 🔒 Security Policy

## Supported versions

This is a personal research project. Only the latest `main` branch is supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| older   | :x:                |

## Design notes (why risk is low by default)

- 🔌 **Fully local**: Ollama + Qdrant + Streamlit run on `localhost` / a Docker bridge network. No cloud API keys, no telemetry.
- 🔑 **No credentials in repo**: configuration is via `.env` (gitignored). `.env.example` contains only non-sensitive defaults.
- 📦 **Pinned images**: `ollama/ollama:0.33.1`, `qdrant/qdrant:v1.19.1`, `python:3.13-slim`, `uv:0.12.10`. Bump deliberately and re-test.

## Reporting a vulnerability 🚨

**Do not open a public issue for security reports.**

1. Use GitHub **Private vulnerability reporting** (Security tab → Report a vulnerability), or contact the maintainer privately.
2. Include: affected file/commit, steps to reproduce, impact, and any suggested fix.
3. Expect an acknowledgement within **7 days**. We will coordinate a fix and disclosure timeline with you.

## Good hygiene for contributors 🧹

- 🚫 Never commit `.env`, `*.pem`, tokens, or model binaries. Check `git status` before pushing.
- 🔍 Corpus files under `data/raw/` are gitignored — do not force-add them.
- 🐳 Do not publish the dev ports (6333, 11434, 8501) beyond localhost without authentication.
- ⬆️ Keep base images and `uv.lock` up to date; run `make lint test` before opening a PR.

## Scope

Out of scope: the EU AI Act text itself (public law, mirrored at setup), upstream model weights, and third-party image vulnerabilities (report those upstream, but tell us so we can bump pins).
