#!/usr/bin/env bash
# Fetch the EU AI Act corpus (English) into data/raw.
# Primary: verbatim Markdown mirror on GitHub (EUR-Lex blocks bots with a WAF
# challenge, so automated PDF download from eur-lex.europa.eu fails with HTTP 202).
# Source text: Regulation (EU) 2024/1689, OJ 12.7.2024. Reuse permitted under
# Commission Decision 2011/833/EU with source acknowledgement (see file header).
set -euo pipefail

mkdir -p data/raw

MD_OUT="data/raw/ai-act-2024-1689-en.md"
MD_URL="https://raw.githubusercontent.com/tjf-trojer/eu-ai-act-map/main/corpora/eu/ai-act-2024-1689-en.md"

if [[ -f "$MD_OUT" ]]; then
  echo "Already present: $MD_OUT"
else
  echo "Downloading EU AI Act EN markdown..."
  curl -fL --retry 3 -o "$MD_OUT" "$MD_URL"
  echo "Saved to $MD_OUT"
fi
ls -lh "$MD_OUT"

# Optional: the authentic OJ PDF. Download it by hand in a browser, as EUR-Lex
# challenges automated clients. Place it in data/raw/ and rerun ingest.
# https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689
