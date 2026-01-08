# History

Linear log of decisions and progress for the ONE‑SHOT PDF→LLM converter. Keep entries chronological and concise.

## 1) Goals and constraints

- Convert a single authoritative PDF into a structured, multi‑file Markdown set optimized for small LLMs.
- Constraints: deterministic outputs, YAML front‑matter everywhere (except README.md), strict atomic units, single ZIP packaging.

## 2) Initial implementation

- Python + PowerShell orchestration; PDF extraction via PyMuPDF/pdfplumber; optional OCR via Tesseract.
- Baseline tests validate reporting, CSV/index consistency, and environment setup.

## 3) Iterations and decisions

- Shifted repo messaging from template to ONE‑SHOT specification alignment.
- Added reporting and docs updates to reflect output expectations.

## 4) Testing and quality gates

- Focus areas: extraction correctness, index consistency, deterministic packaging.
- Gate: tests must pass; outputs validated against spec rules.

## 5) Current state

- Repo aligned to ONE‑SHOT spec with documentation and reporting helpers.
- Pending: oneshot CLI to generate atomic units, enforce front‑matter, validate, and zip.

## 6) Next steps

- Implement oneshot CLI and validators; add domain grouping and front‑matter enforcement; package ZIP.

Guidelines

- Keep it linear and readable; one can reconstruct the project story.
- Link PRs/issues where relevant.
