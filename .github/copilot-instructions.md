# Copilot Instructions for This Repository

This repository is a lightweight template for greenfield PowerShell + Python projects with a clean, test-gated Git workflow. Use this document as high-priority context when assisting within this folder.

## Assumptions
- Shell: Windows PowerShell (`pwsh`). Adapt commands for POSIX when needed.
- Python: Local virtual environment (`.venv`) preferred for installs and runtime.
- Git: Conventional Commits, test-gated commits recommended.

## Quickstart
```powershell
# Option A: One-shot setup
./setup.ps1 -InstallDev

# Option B: Manual
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Helper Scripts
- `git-helper.ps1` (dot-source into current session):
  - `gcb <branch>`: create/switch to feature branch.
  - `gct <message>`: add/commit/push (default message uses Conventional Commits).
  - `gctt <message>`: test-gated commit; prefers `./scripts/task.ps1 -RunTests`, falls back to `pytest` via `.venv`.
  - `gsync`: fetch + pull --rebase.

- `scripts/task.ps1`:
  - Flags: `-Verbose`, `-RunTests`.
  - Prefers `.venv\Scripts\python.exe`; otherwise uses `python` from PATH.
  - Runs `src\main.py`; `-RunTests` executes pytest in `tests`.

- `setup.ps1`:
  - Creates `.venv` (if missing).
  - Installs `requirements.txt`; `-InstallDev` also installs `requirements-dev.txt`.

## Git Workflow (condensed)
- Identity (once per machine):
```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```
- Initialize/connect:
```powershell
git init
git remote add origin https://github.com/<owner>/<repo>.git
git remote -v
```
- Branching & commits:
```powershell
git checkout -b feat/short-task-name
git add -A
git commit -m "feat: concise message"
```
- First push (set upstream):
```powershell
git push -u origin HEAD
```
- Test-gated commit (safer):
```powershell
.\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -eq 0) {
  git add -A
  git commit -m "test: passing suite"
  git push
} else {
  Write-Host "Tests failed; not committing."
}
```
- Pull requests:
```powershell
git fetch --all
git push -u origin HEAD
```
- Recovery basics: `git status`, `git diff`, `git restore`, `git reset --soft HEAD~1`, `git reset --hard HEAD~1`, `git log --oneline --graph --decorate`.

## Commit Messages (Conventional Commits)
- Format: `type(scope)!: subject` (scope/`!` optional; `!` marks breaking changes).
- Common types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `build`, `ci`, `revert`.
- Breaking changes: add `!` and/or footer `BREAKING CHANGE:` explaining impact.
- Examples:
  - `feat(task): add PowerShell task script with -RunTests`
  - `test: add pytest for greet() default and custom`
  - `chore: replace template ignore with .gitignore`
  - `feat(api)!: remove deprecated flags` + footer `BREAKING CHANGE: -OldFlag removed; use -NewFlag`

## Testing
- Pytest (preferred):
```powershell
python -m pytest -q tests
python -m pytest tests/test_main.py -q
python -m pytest tests/test_main.py::test_greet_default -q
```
- Use `gctt` for test-gated commits; it runs tests then commits/pushes only on pass.

## Project Structure (suggested)
```
repo-root/
  src/                # Python source (e.g., main.py, __init__.py)
  scripts/            # PowerShell helpers (e.g., task.ps1)
  tests/              # Test suite (pytest)
  requirements.txt    # Runtime deps
  requirements-dev.txt# Dev/test deps
  .env                # Local secrets (ignored)
  .gitignore
  setup.ps1
  git-helper.ps1
  PROMPT.md
  README.md
```

## Guardrails
- Secrets: never commit real secrets; keep in `.env` (ignored).
- TLS: prefer CA bundles over disabling verification.
```powershell
$env:REQUESTS_CA_BUNDLE = 'C:\path\to\company_ca.pem'
```
- `.gitignore`: keep venv, caches, logs, and node_modules out of Git.
- Windows scripts: you may need to allow and unblock local scripts:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Unblock-File .\git-helper.ps1
Unblock-File .\scripts\task.ps1
Unblock-File .\setup.ps1
```

## Assistant Behavior (for Copilot/agents)
- Prefer `.venv\Scripts\python.exe` when running Python.
- Use small, surgical patches; avoid broad refactors unless requested.
- Run tests after code changes; gate commits when feasible.
- Respect `.gitignore` and never add secrets.
- For context refresh: enumerate workspace (`list_dir`), then read pinned files (PROMPT.md, README.md, git-helper.ps1, setup.ps1, scripts/task.ps1, src/main.py, tests/test_main.py, TESTING.md).
- Keep answers concise and actionable; include PowerShell commands in fenced blocks.

## Optional: Bootstrap Pattern
- If `assistant-context.md` exists, read it first for pinned files/rules.
- An `assistant-bootstrap.ps1` can summarize the workspace and invoke `./setup.ps1 -InstallDev`.
- A `.vscode/tasks.json` task can run the bootstrap via `pwsh -File assistant-bootstrap.ps1`.

## References
- `PROMPT.md`: venv quickstart, condensed Git workflow, commands, and template guidance.
- `README.md`: helper usage, setup, Git essentials, and conventional commits.
- `TESTING.md`: environment, install, run tests, patterns, and troubleshooting.
