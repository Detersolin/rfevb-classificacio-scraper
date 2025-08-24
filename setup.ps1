# Instal·lació al PC: clona/actualitza repo, crea venv, deps i tasca programada
param(
  [string]$RepoURL = "https://github.com/EL_TEU_USUARI/rfevb-classificacio-scraper.git",
  [string]$InstallDir = "C:\Overlay\rfevb-classificacio-scraper"
)

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Cal Git instal·lat (git-scm.com)" }
if (-not (Get-Command py  -ErrorAction SilentlyContinue)) { throw "Cal Python instal·lat (python.org). Marca 'Add Python to PATH'." }

if (Test-Path $InstallDir) {
  Set-Location $InstallDir
  git pull
} else {
  git clone $RepoURL $InstallDir
  Set-Location $InstallDir
}

py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

New-Item -ItemType Directory -Force -Path "C:\Overlay" | Out-Null

# Crea tasca programada que arrenca el scraper a l'inici de sessió
$taskName = "RFEVB_Clasif_Scraper"
$ps1 = Join-Path $InstallDir "run_scraper.ps1"
$action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ps1`" -RepoDir `"$InstallDir`""
schtasks /Create /TN $taskName /TR $action /SC ONLOGON /RL HIGHEST /F

Write-Host "✔ Instal·lació completa. Reinicia sessió o executa ara: $action"
