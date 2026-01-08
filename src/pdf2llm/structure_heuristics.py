from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class Block:
    page: int
    type: str  # heading|paragraph|list_item|code
    text: str
    level: int = 0  # for headings


_re_heading = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")
_re_list = re.compile(r"^(?:[-*•]\s+|\d+\.\s+)(.+)$")


def _infer_heading_level(line: str) -> int:
    m = _re_heading.match(line.strip())
    if m:
        dot_count = m.group(1).count(".")
        return min(6, dot_count + 2)  # start at h2 by default
    # fallback: short, title-ish lines as h2
    if 0 < len(line.strip()) <= 60 and line.strip()[0].isupper() and line.strip().endswith(":"):
        return 2
    return 0


def _is_code_line(line: str) -> bool:
    if line.startswith("    "):
        return True
    # many non-alnum chars may indicate code
    non_alnum = sum(1 for c in line if not c.isalnum() and c not in {" ", "_"})
    return non_alnum > max(10, len(line) // 3)


def parse_page_text(page: int, text: str) -> List[Block]:
    blocks: List[Block] = []
    lines = text.splitlines()
    i = 0
    in_code = False
    code_buf: List[str] = []
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "```":
            if in_code:
                blocks.append(Block(page=page, type="code", text="\n".join(code_buf)))
                code_buf.clear()
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(ln)
            i += 1
            continue

        if not ln.strip():
            i += 1
            continue

        level = _infer_heading_level(ln)
        if level:
            title = _re_heading.sub(r"\2", ln).strip() if _re_heading.match(ln) else ln.strip().rstrip(":")
            blocks.append(Block(page=page, type="heading", text=title, level=level))
            i += 1
            continue

        m = _re_list.match(ln)
        if m:
            blocks.append(Block(page=page, type="list_item", text=m.group(1).strip()))
            i += 1
            continue

        if _is_code_line(ln):
            # collect consecutive code-ish lines
            code_lines = [ln]
            j = i + 1
            while j < len(lines) and _is_code_line(lines[j]):
                code_lines.append(lines[j])
                j += 1
            blocks.append(Block(page=page, type="code", text="\n".join(code_lines)))
            i = j
            continue

        # paragraph: collect until blank line
        para_lines = [ln]
        j = i + 1
        while j < len(lines) and lines[j].strip():
            # stop paragraph if next line is clear heading/list start
            if _infer_heading_level(lines[j]) or _re_list.match(lines[j]) or _is_code_line(lines[j]):
                break
            para_lines.append(lines[j])
            j += 1
        blocks.append(Block(page=page, type="paragraph", text=" ".join(x.strip() for x in para_lines)))
        i = j
    return blocks


def write_blocks_jsonl(blocks: Iterable[Block], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for b in blocks:
            f.write(json.dumps({
                "page": b.page,
                "type": b.type,
                "text": b.text,
                "level": b.level,
            }, ensure_ascii=False) + "\n")
