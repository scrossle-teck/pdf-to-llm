from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import json
import os

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Lazy optional dependency


@dataclass
class StageRouting:
    engine: str = "none"  # none|heuristic|local-small|cloud-small|frontier
    sample_rate: float = 0.0
    max_tokens: int = 0
    escalate_when: list[str] = field(default_factory=list)
    escalate_to: Optional[str] = None
    escalate_cap: int = 0


@dataclass
class ModelRouting:
    defaults: Dict[str, str] = field(default_factory=lambda: {"provider": "none"})
    stages: Dict[str, StageRouting] = field(
        default_factory=lambda: {
            "structure": StageRouting(engine="heuristic", sample_rate=0.0),
            "tables": StageRouting(engine="heuristic", sample_rate=0.0),
            "figures": StageRouting(engine="none", sample_rate=0.0),
            "qa": StageRouting(engine="none", sample_rate=0.0),
        }
    )


@dataclass
class OCRConfig:
    mode: str = "auto"  # on|auto|off
    lang: str = "eng"


@dataclass
class ChunkingConfig:
    target_tokens: int = 3000
    overlap_tokens: int = 200


@dataclass
class PipelineConfig:
    input: Optional[str] = None
    output_dir: str = "out"
    concurrency: int = 4
    ocr: OCRConfig = field(default_factory=OCRConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    models: ModelRouting = field(default_factory=ModelRouting)
    budgets: Dict[str, int] = field(
        default_factory=lambda: {"per_document_tokens": 400_000, "daily_tokens": 2_000_000}
    )


def default_config() -> PipelineConfig:
    return PipelineConfig()


def _as_dict(cfg: PipelineConfig) -> dict:
    def to_dict(obj):
        if hasattr(obj, "__dict__"):
            return {k: to_dict(v) for k, v in obj.__dict__.items()}
        if isinstance(obj, (list, tuple)):
            return [to_dict(v) for v in obj]
        return obj

    return to_dict(cfg)


def save_config(cfg: PipelineConfig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _as_dict(cfg)
    if path.suffix.lower() in {".yaml", ".yml"} and yaml is not None:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_config(path: Optional[Path]) -> PipelineConfig:
    if path is None:
        return default_config()
    if not path.exists():
        return default_config()
    text = path.read_text(encoding="utf-8")
    data: dict
    if path.suffix.lower() in {".yaml", ".yml"} and yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text or "{}")

    def get_nested(d: dict, key: str, default):
        return d.get(key, default)

    cfg = PipelineConfig()
    cfg.input = data.get("input", cfg.input)
    cfg.output_dir = data.get("output_dir", cfg.output_dir)
    cfg.concurrency = int(data.get("concurrency", cfg.concurrency))

    ocr = get_nested(data, "ocr", {})
    mode_val = ocr.get("mode", cfg.ocr.mode)
    if isinstance(mode_val, bool):
        cfg.ocr.mode = "on" if mode_val else "off"
    else:
        cfg.ocr.mode = str(mode_val)
    cfg.ocr.lang = ocr.get("lang", cfg.ocr.lang)

    chunk = get_nested(data, "chunking", {})
    cfg.chunking.target_tokens = int(chunk.get("target_tokens", cfg.chunking.target_tokens))
    cfg.chunking.overlap_tokens = int(chunk.get("overlap_tokens", cfg.chunking.overlap_tokens))

    budgets = get_nested(data, "budgets", cfg.budgets)
    cfg.budgets = {k: int(v) for k, v in budgets.items()}

    models = get_nested(data, "models", {})
    cfg.models.defaults = get_nested(models, "defaults", cfg.models.defaults)
    stages = get_nested(models, "stages", {})
    for name, st in stages.items():
        current = cfg.models.stages.get(name, StageRouting())
        current.engine = st.get("engine", current.engine)
        current.sample_rate = float(st.get("sample_rate", current.sample_rate))
        current.max_tokens = int(st.get("max_tokens", current.max_tokens))
        current.escalate_when = list(st.get("escalate_when", current.escalate_when))
        current.escalate_to = st.get("escalate_to", current.escalate_to)
        current.escalate_cap = int(st.get("escalate_cap", current.escalate_cap))
        cfg.models.stages[name] = current

    return cfg


def resolve_output_root(cfg: PipelineConfig, explicit_out: Optional[Path]) -> Path:
    base = Path(explicit_out or cfg.output_dir)
    return base


def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}
