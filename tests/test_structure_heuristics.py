import os
import sys
from pathlib import Path

# Ensure src is on import path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from pdf2llm.structure_heuristics import parse_page_text


def test_parse_page_text_basic():
    text = """
1. Introduction
- Bullet item one
- Bullet item two

Code block:
    def foo():
        return 42

A regular paragraph follows with some words.
    """.strip()

    blocks = parse_page_text(1, text)
    types = [b.type for b in blocks]
    assert "heading" in types, "Heading should be detected"
    assert types.count("list_item") >= 2, "List items should be detected"
    assert "code" in types, "Code block should be detected"
    assert "paragraph" in types, "Paragraph should be detected"
