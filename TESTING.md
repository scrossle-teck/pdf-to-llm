# Testing (Template)

Reusable guidance for future Python projects.

## 1) Environment

- Create a venv and keep deps local to the repo.
- Pin runtime deps in `requirements.txt`; test deps in `requirements-dev.txt`.

## 2) Install

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## 3) Run tests

```powershell
python -m pytest -q
```

## 4) Targeted runs

```powershell
python -m pytest tests/test_some_file.py -q
python -m pytest tests/test_some_file.py::test_specific -q
```

## 5) Patterns

- Prefer unit tests with fakes/mocks over live calls.
- Normalize paths with `pathlib` for cross‑platform assertions.
- Validate config/manifest shapes with JSON Schema when helpful.
- Use `monkeypatch` to override env or swap out side‑effecting calls.

## 6) Test‑gated commits (PowerShell helper)

```powershell
. .\git-helper.ps1
gctt "test: passing suite"
```

## 7) Troubleshooting

- If imports fail, ensure venv is active and deps are installed.
- If tests write files, prefer `tmp_path` fixtures to isolate side effects.
- Re-run a failing test with `-k` and `-s` for debug output.

That’s it — keep tests fast, focused, and reliable.
