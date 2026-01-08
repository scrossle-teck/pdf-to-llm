
# Conversion Rules (Non-Negotiable)

1. **Treat the PDF as canonical truth.**
2. **No reinterpretation or summarization.** Preserve ambiguity explicitly.
3. **Atomicity:** Exactly **one executable unit per file**.
4. **Front-matter:** Mandatory in every Markdown file **except** `README.md`.
5. **Index:** `index.md` is machine-oriented with `type: index`; **no tutorials**.
6. **Examples:** All examples must be **verbatim** from the PDF.
7. **Parameters:** Preserve required/optional, types, positions, enums, wildcards, streaming behavior.
8. **Boilerplate:** Remove repeated global material from executable files; normalize into `shared/common-concepts.md`.
9. **Chunk size:** Target **~500–1200 tokens per file** where feasible.
10. **Directory names:** Must be functional groupings found in the PDF.
11. **Filenames:** Must be **exact symbolic identifiers** (e.g., `POST_Login.md`).
12. **State effect:** Set `creates|updates|deletes|queries|none` accurately per unit.
13. **Source citation:** Front-matter `source.type=pdf`, `source.title`, `source.section` populated when known.
14. **Root packaging:** Single top-level directory: `<subject>-docs/`.
15. **ZIP:** Delivered as exactly **one** ZIP: `<inferred-subject>-llm-optimized-docs.zip`.
16. **README.md:** Human-facing prose, **no front-matter**, **not for LLM ingestion**.
17. **Determinism:** All generation must be driven by canonical line ranges; no cross-file hallucination.
18. **Validation:** Before zipping, confirm:
    - README exists; no front-matter
    - index.md exists; has front-matter
    - Every other file has valid front-matter as first block
    - One atomic unit per file
    - Parameters preserved
    - Examples verbatim
    - Boilerplate normalized to `shared/common-concepts.md`
    - ZIP contains exactly one top-level directory
