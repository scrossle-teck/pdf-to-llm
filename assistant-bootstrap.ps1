param(
    [switch]$InstallDev
)

Write-Host "[assistant] Bootstrap starting..." -ForegroundColor Cyan

# Show workspace summary
Write-Host "[assistant] Workspace: $PWD" -ForegroundColor Cyan
Get-ChildItem -Force | Select-Object Name, Length | Format-Table -AutoSize

# Read assistant-context.md if present
$ctxPath = Join-Path $PWD "assistant-context.md"
if (Test-Path $ctxPath) {
    Write-Host "[assistant] Reading assistant-context.md" -ForegroundColor Cyan
    Get-Content $ctxPath | Write-Output
} else {
    Write-Host "[assistant] No assistant-context.md found." -ForegroundColor Yellow
}

# Optionally run setup
if ($InstallDev) {
    $setup = Join-Path $PWD "setup.ps1"
    if (Test-Path $setup) {
        Write-Host "[assistant] Running setup.ps1 -InstallDev" -ForegroundColor Cyan
        & $setup -InstallDev
    } else {
        Write-Host "[assistant] setup.ps1 not found; skipping." -ForegroundColor Yellow
    }
}

# Try running tests via task script if present
$task = Join-Path $PWD "scripts\task.ps1"
if (Test-Path $task) {
    Write-Host "[assistant] Running tests via scripts\\task.ps1 -RunTests" -ForegroundColor Cyan
    & $task -RunTests
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[assistant] Tests passed." -ForegroundColor Green
    } else {
        Write-Host "[assistant] Tests failed (exit $LASTEXITCODE)." -ForegroundColor Red
    }
} else {
    Write-Host "[assistant] No scripts\\task.ps1 found; skipping test run." -ForegroundColor Yellow
}

Write-Host "[assistant] Bootstrap complete." -ForegroundColor Green
