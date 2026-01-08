# Git helper functions
# Dot-source this file to load the helper functions into your current PowerShell session:
#   . $PSScriptRoot\git-helper.ps1
# Or specify the path explicitly:
#   . "C:\\path\\to\\git-helper.ps1"

function Get-ProjectPython {
  $venvPy = Join-Path (Get-Location) ".venv\Scripts\python.exe"
  if (Test-Path $venvPy) { return $venvPy }
  return "python"
}

function Get-TaskScriptPath {
  $taskPath = Join-Path (Get-Location) "scripts\task.ps1"
  if (Test-Path $taskPath) { return $taskPath }
  return $null
}

function gct {
  param([string]$m = "feat: update")
  git add -A
  git commit -m $m
  git push
}

function gctt {
  param([string]$m = "test: passing suite")
  $task = Get-TaskScriptPath
  if ($null -ne $task) {
    Write-Host "[gctt] Running task script tests: $task -RunTests" -ForegroundColor Cyan
    & $task -RunTests
  } else {
    $py = Get-ProjectPython
    Write-Host "[gctt] Running pytest via: $py" -ForegroundColor Cyan
    & $py -m pytest -q
  }

  if ($LASTEXITCODE -eq 0) {
    git add -A
    git commit -m $m
    git push
  } else {
    Write-Host "Tests failed; not committing." -ForegroundColor Red
    return $LASTEXITCODE
  }
}

function gcb {
  param([Parameter(Mandatory = $true)][string]$name)
  git checkout -b $name
}

function gsync {
  git fetch --all
  git pull --rebase
}

# Optional: add these to your profile for auto-loading at shell start
# New-Item -Force -ItemType File -Path $PROFILE | Out-Null
# Add-Content -Path $PROFILE -Value ". $PSScriptRoot\\git-helper.ps1"
