<#
.SYNOPSIS
    Проверяет окружение Visual Studio и Windows SDK на наличие критических компонентов.
.DESCRIPTION
    Диагностический скрипт для поиска причин ошибок линковки (kernel32.lib и др.).
    Проверяет: установленные версии VS / Windows SDK / MSVC toolchain, наличие файлов.
.EXAMPLE
    .\scripts\verify-environment.ps1
#>

$ErrorActionPreference = "Continue"
$foundIssues = @()

Write-Host "=== Visual Studio Environment Verification ===" -ForegroundColor Cyan
Write-Host ""

# --- Проверка VS где угодно ---
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
$vsPreviewWhere = "${env:ProgramFiles}\Microsoft Visual Studio\Installer\vswhere.exe"

$vswherePath = $null
if (Test-Path $vsWhere) { $vswherePath = $vsWhere }
elseif (Test-Path $vsPreviewWhere) { $vswherePath = $vsPreviewWhere }

if ($vswherePath) {
    Write-Host "[OK] vswhere.exe найден: $vswherePath" -ForegroundColor Green
    $vsInfo = & $vswherePath -products * -format json | ConvertFrom-Json
    if ($vsInfo) {
        foreach ($vs in $vsInfo) {
            Write-Host "     Установка: $($vs.displayName) [$($vs.catalog.productLineVersion)]" -ForegroundColor Gray
            Write-Host "     Путь: $($vs.installationPath)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "[WARN] vswhere.exe не найден. Visual Studio может быть не установлена." -ForegroundColor Yellow
    $foundIssues += "vswhere.exe not found"
}

Write-Host ""

# --- Проверка Windows SDK ---
$sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10"
$sdkPath2 = "${env:ProgramFiles}\Windows Kits\10"

$kitPath = $null
if (Test-Path $sdkPath) { $kitPath = $sdkPath }
elseif (Test-Path $sdkPath2) { $kitPath = $sdkPath2 }

if ($kitPath) {
    Write-Host "[OK] Windows Kits найден: $kitPath" -ForegroundColor Green
    $sdkVersions = Get-ChildItem "$kitPath\lib" -Directory -ErrorAction SilentlyContinue
    if ($sdkVersions) {
        foreach ($ver in $sdkVersions) {
            $umPath = "$kitPath\lib\$($ver.Name)\um\x64\kernel32.lib"
            if (Test-Path $umPath) {
                Write-Host "     SDK $($ver.Name): kernel32.lib найден" -ForegroundColor Green
            } else {
                Write-Host "     SDK $($ver.Name): kernel32.lib ОТСУТСТВУЕТ!" -ForegroundColor Red
                $foundIssues += "kernel32.lib not found for SDK $($ver.Name)"
            }
        }
    }
} else {
    Write-Host "[ERROR] Windows Kits 10 не найден!" -ForegroundColor Red
    $foundIssues += "Windows Kits 10 not found"
}

Write-Host ""

# --- Проверка MSVC toolchain ---
$msvcBase = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"
$msvcBase2 = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC"
$msvcBase3 = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2017\BuildTools\VC\Tools\MSVC"
# Также проверим редакции Community/Professional/Enterprise
$editions = @("Community", "Professional", "Enterprise", "BuildTools")
$vsYears = @("2025", "2022", "2019", "2017")

$msvcFound = $false
foreach ($year in $vsYears) {
    foreach ($ed in $editions) {
        $base = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\$year\$ed\VC\Tools\MSVC"
        if (Test-Path $base) {
            $versions = Get-ChildItem $base -Directory -ErrorAction SilentlyContinue
            if ($versions) {
                $msvcFound = $true
                foreach ($v in $versions) {
                    Write-Host "[OK] MSVC $($v.Name) (VS $year $ed)" -ForegroundColor Green
                    $libPath = "$base\$($v.Name)\lib\x64"
                    if (Test-Path "$libPath\vcruntime.lib") {
                        Write-Host "     vcruntime.lib найден" -ForegroundColor Green
                    } else {
                        Write-Host "     vcruntime.lib ОТСУТСТВУЕТ!" -ForegroundColor Red
                        $foundIssues += "vcruntime.lib not found in $libPath"
                    }
                }
            }
        }
    }
}

if (-not $msvcFound) {
    Write-Host "[ERROR] MSVC toolchain не найден!" -ForegroundColor Red
    $foundIssues += "MSVC toolchain not found"
}

Write-Host ""

# --- Проверка переменных окружения ---
$envVars = @("VC_IncludePath", "VC_LibraryPath_x64", "WindowsSDK_IncludePath",
             "WindowsSDK_LibraryPath_x64", "NETFXKitsDir", "VC_ExecutablePath_x64")
foreach ($var in $envVars) {
    $val = [Environment]::GetEnvironmentVariable($var, "Process")
    if ($val) {
        Write-Host "[OK] $var = $val" -ForegroundColor Green
    } else {
        Write-Host "[INFO] $var не задана (нормально вне dev-командной строки)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Итог ===" -ForegroundColor Cyan
if ($foundIssues.Count -eq 0) {
    Write-Host "Проблем не обнаружено." -ForegroundColor Green
} else {
    Write-Host "Найдено проблем: $($foundIssues.Count)" -ForegroundColor Red
    foreach ($issue in $foundIssues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Рекомендация: запустите Visual Studio Installer и убедитесь, что компоненты" -ForegroundColor Yellow
    Write-Host "'Desktop development with C++' и Windows SDK установлены." -ForegroundColor Yellow
}
