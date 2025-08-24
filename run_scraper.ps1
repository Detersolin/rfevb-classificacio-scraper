# Executa el scraper amb entorn virtual dins del repo i actualitza dependències
param(
  [string]$RepoDir = "C:\Overlay\rfevb-classificacio-scraper"
)

$ErrorActionPreference = "SilentlyContinue"

if (Test-Path $RepoDir) {
  Set-Location $RepoDir
  git pull
} else {
  Write-Host "Repo no trobat a $RepoDir"
  exit 1
}

if (-not (Test-Path ".\.venv")) {
  py -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

New-Item -ItemType Directory -Force -Path "C:\Overlay" | Out-Null

# Arrenca el scraper (bucle continu)
.\.venv\Scripts\python.exe .\scrape_classificacio.py
