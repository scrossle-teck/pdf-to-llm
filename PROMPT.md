# Workspace Prompt — PowerShell + Python Template

Use the project's virtual environment for all Python work and keep a clean, recoverable Git history. This prompt provides copy/paste commands to get started quickly.

Why

- Isolated and reproducible Python dependencies via `.venv`.
- Consistent commits and an easy-to-navigate Git history.

PowerShell quickstart (copy/paste):

```powershell
# Create venv (first time only)
python -m venv .venv

# Activate venv in current PowerShell session
. .\.venv\Scripts\Activate.ps1

# Install runtime requirements (if present)
python -m pip install -r requirements.txt

# Install dev/test requirements (if present)
python -m pip install -r requirements-dev.txt

# Run tests (if using pytest)
python -m pytest -q tests

# Example: run your Python entry point
# Adjust to your project layout (module, script, etc.)
python src\main.py

# Example: run a PowerShell helper script
./scripts/task.ps1 -Verbose
```

Notes

- When scripting from outside an activated session, prefer the full path to the venv Python, e.g.: `C:\path\to\repo\.venv\Scripts\python.exe -m pytest -q`.
- On POSIX shells, activate with `source .venv/bin/activate`.
- Keep virtual environment, caches, and secrets out of Git (see `.gitignore`).

.env recommendations

Place secrets and configuration in a `.env` file in the repo root and do not commit it. Example variable names:

```text
APP_BASE_URL=https://example.local
APP_USER=you@example.com
APP_TOKEN=your_token_here
```

Applications should read configuration from environment variables (or a local `.env` loader) rather than hardcoding secrets.

Network/TLS note

If your environment uses TLS interception (corporate proxy), configure a CA bundle and point Python requests to it:

```powershell
$env:REQUESTS_CA_BUNDLE = 'C:\path\to\company_ca.pem'
```

Git workflow

For day-to-day version control, use this condensed workflow:

- Branching: commit directly to `main` or create a feature branch per task.

  ```powershell
  git checkout -b feat/short-task-name
  ```

- Identity: configure once per machine.

  ```powershell
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  git config --global init.defaultBranch main
  ```

- Init/connect: create a repo and add a remote (optional).

  ```powershell
  git init
  git remote add origin https://github.com/<owner>/<repo>.git
  git remote -v

  ```

- Commit messages: follow Conventional Commits.
  - Format: `type(scope)!: subject` (scope/`!` optional; `!` marks breaking changes).
  - Common types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `build`, `ci`, `revert`.
  - Examples:
    - `feat(task): add PowerShell task script with -RunTests`
    - `test: add pytest for greet() default and custom`
    - `chore: replace template ignore with .gitignore`
    - `feat(api)!: remove deprecated flags`
      Footer: `BREAKING CHANGE: -OldFlag removed; use -NewFlag`
- Push policy: first push on a new branch sets upstream.

  ```powershell
  git push -u origin HEAD
  ```

- Test-gated commits (safer): only commit when tests pass.

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

- PRs: fetch, push branch, open a PR in your host UI.

  ```powershell
  git fetch --all
  git push -u origin HEAD
  ```

- Recovery: `git status`, `git diff`, `git restore`, and `git reset` (soft/hard) help undo mistakes.
  Use `git log --oneline --graph --decorate` to browse history.

Assistant-driven auto-commit (optional)

- Provide explicit permission for Git operations.
- Define branch policy, message convention, and push behavior.
- Decide whether to test-gate commits; ensure `.gitignore` excludes secrets.
- Assistant can add/commit per logical chunk and push to upstream.

Project structure (suggested)

```text
repo-root/
  src/                # Python source
  scripts/            # PowerShell helpers
  tests/              # Test suite (pytest)
  requirements.txt    # Runtime deps
  requirements-dev.txt# Dev/test deps
  .env                # Local secrets (ignored)
  .gitignore
  PROMPT.md           # This file
  README.md
```

Assistant reminder

Prefer the project's `.venv` Python executable for installs and runtime checks. Align commit behavior and messages with the Git workflow in this prompt.
