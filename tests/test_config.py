"""Smoke tests that need no services."""

from pathlib import Path
import json


def test_gold_qa_is_valid():
    items = json.loads(Path("data/gold_qa.json").read_text(encoding="utf-8"))
    assert len(items) >= 10
    for item in items:
        assert item["id"] and item["question"] and item["expected_keywords"]


def test_env_example_has_required_keys():
    text = Path(".env.example").read_text(encoding="utf-8")
    for key in ("LLM_MODEL", "LLM_NUM_CTX", "EMBED_MODEL", "COLLECTION", "TOP_K", "SCORE_THRESHOLD"):
        assert key in text
