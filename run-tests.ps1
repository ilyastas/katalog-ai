# 🚀 Quick Test Script for Windows PowerShell

Write-Host "🧪 KATALOG-AI TEST RUNNER" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Check if venv activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "   Activating .venv..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "📦 Installing test dependencies..." -ForegroundColor Yellow
python -m pip install pytest pytest-cov pytest-asyncio httpx --quiet

Write-Host ""
Write-Host "🧪 Running tests..." -ForegroundColor Cyan
Write-Host ""

# Run tests
python -m pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed (exit code: $exitCode)" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Coverage report generated: htmlcov/index.html" -ForegroundColor Cyan
Write-Host ""

# Ask to open coverage report
$response = Read-Host "Open coverage report in browser? (y/n)"
if ($response -eq 'y') {
    Start-Process htmlcov/index.html
}

exit $exitCode
