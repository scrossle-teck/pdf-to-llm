# Greenfield Powershell + Python Project — Starter Artifacts

This folder includes reusable artifacts to bootstrap new projects with a clean Git workflow and helper commands. See `PROMPT.md` for the condensed Git workflow and quickstart.

## Files

- `.gitignore` — Template ignore rules for Python/PowerShell projects.
- `git-helper.ps1` — PowerShell helper functions for commits and test-gated commits.
- `.editorconfig` — Auto-loaded formatting rules (4-space indent, CRLF, final newline; preserves markdown trailing spaces).

## Quick use

1) Use the ignore template

    `.gitignore` is already provided. Copy it into new repos as needed.

2) Load helper functions for this session

    ```powershell
    . .\git-helper.ps1
    ```

3) (Optional) Auto-load helper on shell start

    ```powershell
    New-Item -Force -ItemType File -Path $PROFILE | Out-Null
    Add-Content -Path $PROFILE -Value ". $PWD\git-helper.ps1"
    ```

4) (Optional) Allow scripts to run (execution policy)

    Some environments restrict running scripts. You can enable a safe policy and unblock local files:

    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    Unblock-File .\git-helper.ps1
    Unblock-File .\scripts\task.ps1
    Unblock-File .\setup.ps1
    ```

Tip: Use `$PSScriptRoot` when these files live in a fixed location you source from.

## Helper usage

- Create and switch to a feature branch:

  ```powershell
  gcb feat/your-branch
  ```

- Commit + push quickly:

  ```powershell
  gct "feat: implement X"
  ```

- Test-gated commit (runs pytest, only commits on pass):

  ```powershell
  gctt "test: passing suite"
  ```

  Note: `gctt` prefers `./scripts/task.ps1 -RunTests` when available; otherwise it falls back to running `pytest` via the project `.venv`.

- Sync from remote:

  ```powershell
  gsync
  ```

## Next steps

- Read `PROMPT.md` for identity, remote, branching, push policy, and recovery.
- Consider creating project-specific variants of these files as needed.

## Python + PowerShell Quickstart

For a small PowerShell-with-Python project, use a local venv and keep dependencies isolated. See `PROMPT.md` for full details.

```powershell
# Create venv (first time only)
python -m venv .venv

# Activate venv for this session
. .\.venv\Scripts\Activate.ps1

# Install dependencies (if present)
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
# PDF → LLM Optimized Docs — ONE‑SHOT Converter

This repository is for a STRICT technical documentation conversion tool that ingests a single authoritative PDF and produces a structured, high‑fidelity Markdown documentation set optimized for SMALL LLMs. It is deterministic, retrieval‑safe, and packaged as one ZIP.

Key goals:
- Semantically lossless conversion (instructions, parameters, examples, constraints)
- Optimized for small LLMs (GPT‑4.1, GPT‑4o, GPT‑5 mini)
- Deterministic outputs with strict chunking (500–1200 tokens/file)
- YAML front‑matter enforced in all files except README.md
- Exactly one top‑level directory packaged in one ZIP

## Output Package

ZIP name:

```
<inferred-subject>-llm-optimized-docs.zip
```

Root directory structure:

```
<inferred-subject>-docs/
├── README.md                  # Human-facing installation & usage (no front‑matter)
├── index.md                   # Machine-oriented navigation index (has front‑matter)
├── <domain-1>/
├── <domain-2>/
├── ...
└── shared/
    └── common-concepts.md
```

Rules:
- Multiple files ONLY (no monolithic docs)
- Exactly ONE atomic unit per file
- Directory names = functional groupings found in the PDF
- Filenames = exact symbolic identifiers (command name, API name, function name)

## Front‑Matter Schema (Required Everywhere Except README.md)

Each Markdown file MUST begin with YAML front‑matter as the FIRST content:

```yaml
---
title: <exact symbolic name>
type: <command|endpoint|function|concept|reference|index>
product: <inferred product/system name>
vendor: <inferred vendor, if present>
language: <CLI or programming language if applicable>
domain: <functional grouping>
llm_use: <procedural|reference|conceptual>
prerequisites:
  - <explicit dependencies or setup>
inputs: <string|list|none>
outputs: <string|list|none>
state_effect: <creates|updates|deletes|queries|none>
tags:
  - <keywords>
source:
  type: pdf
  title: <PDF title>
  section: <PDF section heading if known>
---
```

Omit a field ONLY if truly absent in the PDF. `index.md` MUST use `type: index`. `README.md` MUST NOT include front‑matter.

## Atomic File Body Structure (Executable Units)

Each executable unit file MUST contain:

```
# <Exact Title>

## Purpose
## Prerequisites

## Syntax
```text
<verbatim syntax from PDF>
```

## Parameters / Inputs
- Preserve required vs optional, data types, position/index
- Preserve enumerated/allowed values, pipeline/streaming, wildcard behavior

## Output / Response

## Examples
```text
<ALL examples verbatim from PDF>
```

## Notes
Warnings, constraints, edge cases, REST notes, limits.
```

## Common‑Concept Normalization

Repeated global material (authentication notes, shared constraints, common flags, pagination boilerplate) MUST be:
- Removed from individual files
- Normalized into `shared/common-concepts.md`
- Referenced implicitly, not duplicated

## Fidelity Rules (Non‑Negotiable)

- Treat PDF as canonical truth
- Preserve ambiguity explicitly
- No inferred behavior or invented examples
- No merged files or semantic compression

## Validation Before Zipping

Confirm:
- README.md exists, human‑oriented, no front‑matter
- index.md exists, machine‑oriented, has front‑matter
- Every other file has valid front‑matter as first block
- Each file contains exactly one atomic unit
- Parameter semantics preserved
- Examples are verbatim
- Repeated boilerplate normalized into `shared/common-concepts.md`
- ZIP contains exactly one top‑level directory

## Usage

Environment setup (Windows-first):

```powershell
./setup.ps1 -InstallDev
. ./.venv/Scripts/Activate.ps1
```

Tesseract OCR (optional for scanned PDFs):

```powershell
# If tesseract.exe is not on PATH, set env var
$env:PDF2LLM_TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Project tasks:
- Run tests: `python -m pytest -q tests`
- Generate summary report for an output root (development aid): use `src/report.py` programmatically to produce `report.md` with OCR/tables/figures counts.

The conversion CLI will ingest a single PDF and emit the ZIP with the exact structure above, enforcing front‑matter and atomicity. Packaging and validation are part of the oneshot command.

## Development Notes

- Deterministic outputs and chunk sizes target 500–1200 tokens per file.
- YAML front‑matter is mandatory for all files except `README.md`.
- OCR is used when the PDF contains scanned pages; otherwise text extraction is preferred.
- Tests include report generation and CSV/index consistency checks.

## License & Provenance

This repository produces documentation derived from user‑provided PDFs. Ensure you have rights to process and redistribute resulting docs. Do not commit real secrets.

