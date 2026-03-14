Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Enhanced Voice Assistant Setup"
Write-Host "==================================" -ForegroundColor Cyan

Write-Host "Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue

if (-not $python) {
    Write-Host "Python not found. Install Python 3.11 first." -ForegroundColor Red
    exit 1
}

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

if (!(Test-Path "assets")) {
    New-Item -ItemType Directory -Path assets | Out-Null
}

Write-Host ""
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit .env"
Write-Host "2. Activate venv:"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "3. Run:"
Write-Host "   python main.py"