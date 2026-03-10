# Quick test script for Windows PowerShell

param(
    [switch]$InstallDeps,
    [switch]$OpenCoverage
)

function Test-PythonModule {
    param(
        [string]$Python,
        [string]$ModuleName
    )

    & $Python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('$ModuleName') else 1)" *> $null
    return ($LASTEXITCODE -eq 0)
}

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

$requiredModules = @(
    "pytest",
    "fastapi",
    "sqlalchemy",
    "pydantic",
    "pydantic_settings",
    "httpx",
    "redis",
    "email_validator"
)

$missingModules = @($requiredModules | Where-Object { -not (Test-PythonModule -Python $pythonCmd -ModuleName $_) })

if ($InstallDeps) {
    Write-Host "Installing minimal test dependencies..." -ForegroundColor Yellow
    & $pythonCmd -m pip install pytest pytest-cov pytest-asyncio httpx fastapi sqlalchemy pydantic pydantic-settings redis email-validator --quiet

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Dependency installation failed." -ForegroundColor Red
        exit $LASTEXITCODE
    }
} elseif ($missingModules.Count -gt 0) {
    Write-Host "Missing Python modules: $($missingModules -join ', ')" -ForegroundColor Yellow
    Write-Host "Run .\run-tests.ps1 -InstallDeps to install the minimal test stack." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "Dependency check: OK" -ForegroundColor Green
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
    if ($OpenCoverage) {
        Start-Process $coverageFile
    } else {
        Write-Host "Use .\run-tests.ps1 -OpenCoverage to open it automatically." -ForegroundColor DarkGray
    }
} else {
    Write-Host "Coverage report not found (tests may have failed before report generation)." -ForegroundColor Yellow
}

exit $exitCode
