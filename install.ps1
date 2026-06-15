$REPO_URL = "https://github.com/inzexg-coder/ameni-vs-kernel"
$INSTALL_DIR = "$env:USERPROFILE\.ameni-vs-kernel"
$BIN_DIR = "$env:USERPROFILE\.local\bin"

Write-Host "=== ameni installer (Windows) ===" -ForegroundColor Cyan

if (Test-Path "$INSTALL_DIR\.git") {
    Write-Host "Updating existing installation..." -ForegroundColor Green
    Set-Location $INSTALL_DIR
    git pull --ff-only 2>$null
} else {
    Write-Host "Cloning to $INSTALL_DIR..." -ForegroundColor Green
    git clone --depth=1 $REPO_URL $INSTALL_DIR
}

Write-Host "Installing Python dependency (cryptography)..." -ForegroundColor Green
pip install cryptography 2>$null

if (!(Test-Path $BIN_DIR)) { New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null }

$SHIM_PATH = "$BIN_DIR\ameni.cmd"
@"
@echo off
python "$INSTALL_DIR\server\app.py" %*
"@ | Out-File -FilePath $SHIM_PATH -Encoding ASCII

Write-Host "Installed: $SHIM_PATH" -ForegroundColor Green

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$BIN_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$BIN_DIR", "User")
    Write-Host "Added $BIN_DIR to PATH (reopen terminal)" -ForegroundColor Yellow
}

Write-Host "`nRun: ameni" -ForegroundColor Cyan
