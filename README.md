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

# Run tests (pytest)
python -m pytest -q tests
```

### PDF to LLM CLI (scaffold)

A minimal pipeline CLI is available and can be run end-to-end on a PDF to produce deterministic artifacts (manifest, per-page text):

```powershell
./setup.ps1 -InstallDev
.\.venv\Scripts\python.exe -m pdf2llm --out .\out preflight --pdf .\docs\sample.pdf
.\.venv\Scripts\python.exe -m pdf2llm --out .\out extract   --pdf .\docs\sample.pdf
```

You can also run the whole pipeline via the task script:

```powershell
./scripts/task.ps1 -PdfPath ".\docs\sample.pdf" -OutDir ".\out"
```

### OCR

The pipeline includes an OCR stage that rasterizes pages and extracts text via Tesseract (pytesseract). Use it when PDFs contain scanned pages or low-quality text:

```powershell
# Run only the OCR stage (default DPI 200)
.\.venv\Scripts\python.exe -m pdf2llm --out .\out ocr --pdf .\docs\sample.pdf --dpi 200

# Force re-run even if outputs exist
.\.venv\Scripts\python.exe -m pdf2llm --out .\out ocr --pdf .\docs\sample.pdf --force

# Optional: point directly to tesseract executable if not on PATH
$env:PDF2LLM_TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
.\.venv\Scripts\python.exe -m pdf2llm --out .\out ocr --pdf .\docs\sample.pdf
```

Outputs are written under the deterministic output root:
- `ocr/pNNNNN.txt` — per-page OCR text files
- `ocr.jsonl` — index of OCR results

Notes:
- Tests that require Tesseract will be skipped automatically if it's unavailable.
- DPI can be tuned via `--dpi` for accuracy/speed trade-offs.

## Setup Script (optional)

Run a single script to create the venv and install dependencies (uses the project `.venv` when present):

```powershell
./setup.ps1 -InstallDev
```

- Installs `requirements.txt`; `-InstallDev` also installs `requirements-dev.txt`.
- Falls back to system `python` if `.venv\Scripts\python.exe` is not found.

## Assistant Bootstrap (optional)

- `assistant-context.md`: manifest of pinned files/folders the agent should refresh first.
- `assistant-bootstrap.ps1`: prints a workspace summary, reads `assistant-context.md`, and can run `./setup.ps1 -InstallDev`.
- VS Code task: run via Command Palette — "Assistant: Bootstrap".

```powershell
pwsh -File .\assistant-bootstrap.ps1 -InstallDev
```

## Project Structure (suggested)

```text
repo-root/
  src/                # Python source
  scripts/            # PowerShell helpers
  tests/              # Test suite (pytest)
  requirements.txt    # Runtime deps
  requirements-dev.txt# Dev/test deps
  .env                # Local secrets (ignored)
  .gitignore
  PROMPT.md
  README.md
```

## Dependencies & Testing

- `requirements.txt` — runtime packages.
- `requirements-dev.txt` — dev/test packages (e.g., `pytest`).
- Run tests: `python -m pytest -q tests` (or use `gctt` for test-gated commits).

## Configuration & Secrets

- Keep secrets in `.env` and ensure they are ignored; do not commit.
- Prefer environment variables or a `.env` loader over hardcoding.
- Corporate TLS interception: set a CA bundle for Python requests:

  ```powershell
  $env:REQUESTS_CA_BUNDLE = 'C:\path\to\company_ca.pem'
  ```

## Git Essentials

Use these commands for a clean, recoverable workflow (see `PROMPT.md` for details):

- Identity (once per machine):

  ```powershell
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  git config --global init.defaultBranch main
  ```

- Initialize and connect a repo:

  ```powershell
  git init
  git remote add origin https://github.com/<owner>/<repo>.git
  git remote -v
  ```

- Branching and commits:

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

- Recovery basics:
  `git status`, `git diff`, `git restore`, `git reset --soft HEAD~1`, `git reset --hard HEAD~1`, and `git log --oneline --graph --decorate`.

### Commit Messages (Conventional Commits)

- Format: `type(scope)!: subject` (scope and `!` are optional; `!` marks breaking changes).
- Common types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `build`, `ci`, `revert`.
- Breaking changes: add `!` after type/scope and/or a footer `BREAKING CHANGE:` explaining impact.
- Examples:
  - `feat(task): add PowerShell task script with -RunTests`
  - `test: add pytest for greet() default and custom`
  - `chore: replace template ignore with .gitignore`
  - `feat(api)!: remove deprecated flags` + footer `BREAKING CHANGE: -OldFlag removed; use -NewFlag`

## References

- `PROMPT.md` — venv quickstart, condensed Git workflow, commands, and template guidance.
