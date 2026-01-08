# Learnings (Template)

Use this template to capture meta‑learnings you want to carry into future greenfield projects.

## Design habits to keep

- Separate credentials/config from versioned artifacts (e.g., YAML config + env vars; keep secrets out of VCS).
- Idempotence first: normalize and compare before writing to external systems.
- Prefer typed, structured CLIs (e.g., Click) for testability.
- Make dry-run and confirmation the default safety rails; add `--yes` for automation.
- Prefer CA bundles over disabling TLS verification.

## Testing patterns that scale

- Test with small doubles (dummy clients) instead of hitting real services.
- Use `pytest` fixtures and `monkeypatch` (or mocks) to isolate IO.
- Normalize paths with `pathlib` to stay cross‑platform.
- Add schema checks early for config/manifest shapes.

## Source control discipline

- Commit in small, logical units with clear messages (Conventional Commits help).
- Adopt a test‑gated commit habit for stability.
- Keep `.gitignore` strict about secrets and transient files.

## Documentation cadence

- Keep `README` user-oriented; reference lifecycles (init → edit → run).
- Maintain a linear `HISTORY` for decision tracking.
- Capture “what surprised us” here to speed up the next project.

## Common pitfalls to avoid

- Mixing config and credentials in the same committed file.
- Non-deterministic comparisons causing re-writes (normalize, then hash).
- Platform‑specific path assumptions in tests.
- Over‑scoping: keep core small; defer nice‑to‑haves.
