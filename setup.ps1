param(
    [switch]$InstallDev
)

Write-Host "[setup] Starting environment setup..." -ForegroundColor Cyan

# Ensure Python available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[setup] 'python' not found in PATH. Please install Python." -ForegroundColor Red
    exit 1
}

# Create venv if missing
$venvPath = Join-Path $PWD ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[setup] Creating virtual environment at: $venvPath" -ForegroundColor Yellow
    python -m venv $venvPath
} else {
    Write-Host "[setup] Virtual environment already exists." -ForegroundColor Green
}

# Choose python executable (prefer venv)
$py = if (Test-Path $venvPython) { $venvPython } else { "python" }
Write-Host "[setup] Using Python: $py" -ForegroundColor Cyan

# Install runtime requirements
$req = Join-Path $PWD "requirements.txt"
if (Test-Path $req) {
    Write-Host "[setup] Installing requirements.txt" -ForegroundColor Cyan
    & $py -m pip install -r $req
} else {
    Write-Host "[setup] requirements.txt not found; skipping runtime installs." -ForegroundColor Yellow
}

# Optionally install dev requirements
$reqDev = Join-Path $PWD "requirements-dev.txt"
if ($InstallDev) {
    if (Test-Path $reqDev) {
        Write-Host "[setup] Installing requirements-dev.txt" -ForegroundColor Cyan
        & $py -m pip install -r $reqDev
    } else {
        Write-Host "[setup] requirements-dev.txt not found; skipping dev installs." -ForegroundColor Yellow
    }
}

Write-Host "[setup] Setup complete." -ForegroundColor Green
