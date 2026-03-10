# Quick test script for Windows PowerShell

Write-Host "KATALOG-AI TEST RUNNER" -ForegroundColor Cyan
Write-Host ('=' * 50) -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot
if (-not $root) {
    $root = (Get-Location).Path
}

# Run from repository root even if started from another folder.
Set-Location -Path $root

$venvPython = Join-Path $root ".venv\Scripts\python.exe"

if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "Virtual environment is not activated." -ForegroundColor Yellow
    Write-Host "The script will try to use .venv\\Scripts\\python.exe directly." -ForegroundColor Yellow
}

if (Test-Path $venvPython) {
    $pythonCmd = $venvPython
} else {
    $pythonCmd = "python"
    Write-Host "Warning: .venv Python not found, using system python." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
& $pythonCmd -m pip install pytest pytest-cov pytest-asyncio httpx --quiet

$backendRequirements = Join-Path $root "backend\requirements.txt"
if (Test-Path $backendRequirements) {
    Write-Host "Installing backend requirements..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -r $backendRequirements --quiet

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Backend requirements install failed. Falling back to minimal test dependencies..." -ForegroundColor Yellow
        & $pythonCmd -m pip install fastapi sqlalchemy pydantic pydantic-settings redis email-validator --quiet
    }
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host ""

& $pythonCmd -m pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "All tests passed." -ForegroundColor Green
} else {
    Write-Host "Some tests failed (exit code: $exitCode)." -ForegroundColor Red
}

$coverageFile = Join-Path $root "htmlcov\index.html"
Write-Host ""
if (Test-Path $coverageFile) {
    Write-Host "Coverage report: $coverageFile" -ForegroundColor Cyan
    Write-Host ""

    $response = Read-Host "Open coverage report in browser? (y/n)"
    if ($response -match '^[Yy]$') {
        Start-Process $coverageFile
    }
} else {
    Write-Host "Coverage report not found (tests may have failed before report generation)." -ForegroundColor Yellow
}

exit $exitCode
