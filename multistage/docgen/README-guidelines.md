
# README Guidelines (Authoring Notes)

**Audience:** Human developers/operators

The final `README.md` (placed at `<subject>-docs/README.md`) must:

1. State what the original PDF covered (Commvault 11.36 REST API; operations, endpoints, flows).
2. Describe what the ZIP contains:
   - Split, atomic Markdown files with exact symbolic identifiers per endpoint/command/function.
   - Machine-oriented `index.md` for navigation.
   - `shared/common-concepts.md` consolidating repeated global material.
3. Explain **why files are split**:
   - Deterministic retrieval
   - Lossless chunking for small LLMs
   - One executable unit per file
4. Provide **installation into a fresh project**:
   - Unzip into repository `/docs/commvault-rest-api-docs/`
   - Reference from your build tooling or RAG indexer
5. Describe **VS Code / Copilot usage**:
   - Use Copilot Chat only for mechanical generation from canonical text ranges
   - Do not ask the model to summarize content; enforce templates
6. Optional **RAG usage**:
   - Index per-file chunks
   - Pin `index.md` as the navigation root
   - Treat `README.md` as non-ingestible (exclude in retrievers)
7. **Clear warning**:
   - Preserve file structure and front‑matter exactly
   - Do not merge or compress files
   - Do not edit verbatim examples
