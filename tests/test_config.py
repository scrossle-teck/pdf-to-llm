import os
import sys
from pathlib import Path

# Ensure src on path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from pdf2llm.config import load_config, resolve_output_root, PipelineConfig


def test_load_config_defaults():
    cfg = load_config(None)
    assert isinstance(cfg, PipelineConfig)
    assert cfg.output_dir == "out"
    assert cfg.ocr.mode in {"on", "auto", "off"}


def test_load_config_yaml_override(tmp_path: Path):
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("""
output_dir: custom_out
concurrency: 2
ocr:
  mode: on
chunking:
  target_tokens: 2048
  overlap_tokens: 128
""".strip(), encoding="utf-8")
    cfg = load_config(cfg_path)
    assert cfg.output_dir == "custom_out"
    assert cfg.concurrency == 2
    assert cfg.ocr.mode == "on"
    assert cfg.chunking.target_tokens == 2048
    assert cfg.chunking.overlap_tokens == 128


def test_resolve_output_root(tmp_path: Path):
    cfg = load_config(None)
    root = resolve_output_root(cfg, None)
    assert isinstance(root, Path)
    assert root.name == cfg.output_dir
    explicit = resolve_output_root(cfg, tmp_path / "explicit")
    assert explicit == tmp_path / "explicit"
