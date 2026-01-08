from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> Tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    return h.hexdigest(), size
