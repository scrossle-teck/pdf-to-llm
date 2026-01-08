param(
    [switch]$Verbose,
    [switch]$RunTests
)

Write-Host "[task.ps1] Starting template task..."
if ($Verbose) {
    Write-Host "[task.ps1] Verbose mode enabled." -ForegroundColor Cyan
}

# Example: call Python entry point if present
$pythonPath = Join-Path $PWD ".venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "[task.ps1] Using venv Python at: $pythonPath"
} else {
    $pythonPath = "python"
    Write-Host "[task.ps1] Using system Python from PATH."
}

$mainScript = Join-Path $PWD "src\main.py"
if (Test-Path $mainScript) {
    Write-Host "[task.ps1] Running: $pythonPath $mainScript"
    & $pythonPath $mainScript
} else {
    Write-Host "[task.ps1] No src\\main.py found. Skipping Python run." -ForegroundColor Yellow
}

if ($RunTests) {
    Write-Host "[task.ps1] Running pytest..."
    & $pythonPath -m pytest -q tests
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[task.ps1] Tests passed." -ForegroundColor Green
    } else {
        Write-Host "[task.ps1] Tests failed (exit $LASTEXITCODE)." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "[task.ps1] Task complete."
