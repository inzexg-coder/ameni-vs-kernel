$ErrorActionPreference = "Continue"

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "       $Message" -ForegroundColor Gray
}

$foundIssues = @()

Write-Host "=== Visual Studio Environment Verification ===" -ForegroundColor Cyan
Write-Host ""

# ── vswhere ────────────────────────────────────────────
$vswherePaths = @(
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe",
    "${env:ProgramFiles}\Microsoft Visual Studio\Installer\vswhere.exe"
)
$vswherePath = $null
foreach ($p in $vswherePaths) {
    if (Test-Path $p) { $vswherePath = $p; break }
}

if ($vswherePath) {
    Write-Ok "vswhere.exe: $vswherePath"
    try {
        $vsInfo = & $vswherePath -products * -format json 2>$null | ConvertFrom-Json
        if ($vsInfo -and $vsInfo.Count -gt 0) {
            foreach ($vs in $vsInfo) {
                Write-Info "$($vs.displayName) [$($vs.catalog.productLineVersion)]"
            }
        } else {
            Write-Warn "Visual Studio не найдена через vswhere (возможно, не запускалась ни разу)"
        }
    } catch {
        Write-Warn "Ошибка при вызове vswhere: $_"
    }
} else {
    Write-Warn "vswhere.exe не найден. Visual Studio не обнаружена."
}

Write-Host ""

# ── Windows SDK ────────────────────────────────────────
$sdkPaths = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10",
    "${env:ProgramFiles}\Windows Kits\10"
)
$kitPath = $null
foreach ($p in $sdkPaths) {
    if (Test-Path $p) { $kitPath = $p; break }
}

if ($kitPath) {
    Write-Ok "Windows Kits: $kitPath"
    try {
        $sdkVersions = Get-ChildItem "$kitPath\lib" -Directory -ErrorAction SilentlyContinue
        if ($sdkVersions) {
            foreach ($ver in $sdkVersions) {
                $umPath = "$kitPath\lib\$($ver.Name)\um\x64\kernel32.lib"
                if (Test-Path $umPath) {
                    Write-Info "SDK $($ver.Name): kernel32.lib найден"
                } else {
                    Write-Warn "SDK $($ver.Name): kernel32.lib не найден (возможно, не установлен компонент)"
                    $foundIssues += "kernel32.lib not found for SDK $($ver.Name)"
                }
            }
        } else {
            Write-Warn "В Windows Kits нет lib/ — SDK не установлен"
            $foundIssues += "Windows SDK libraries not found"
        }
    } catch {
        Write-Warn "Ошибка при проверке Windows Kits: $_"
    }
} else {
    Write-Warn "Windows Kits 10 не установлены"
}

Write-Host ""

# ── MSVC ────────────────────────────────────────────────
$editions = @("Community", "Professional", "Enterprise", "BuildTools")
$vsYears = @("2025", "2022", "2019", "2017")
$msvcFound = $false

foreach ($year in $vsYears) {
    foreach ($ed in $editions) {
        $base = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\$year\$ed\VC\Tools\MSVC"
        if (Test-Path $base) {
            try {
                $versions = Get-ChildItem $base -Directory -ErrorAction SilentlyContinue
                if ($versions) {
                    $msvcFound = $true
                    foreach ($v in $versions) {
                        Write-Ok "MSVC $($v.Name) (VS $year $ed)"
                        $libPath = "$base\$($v.Name)\lib\x64"
                        if (Test-Path "$libPath\vcruntime.lib") {
                            Write-Info "vcruntime.lib найден"
                        } else {
                            Write-Warn "vcruntime.lib не найден в $libPath"
                            $foundIssues += "vcruntime.lib not found in $libPath"
                        }
                    }
                }
            } catch {
                # silently continue
            }
        }
    }
}

if (-not $msvcFound) {
    Write-Warn "MSVC toolchain не найден (возможно, не установлен компонент 'Desktop development with C++')"
    $foundIssues += "MSVC toolchain not found — установите через VS Installer"
}

Write-Host ""

# ── Environment variables ──────────────────────────────
$envVars = @("VC_IncludePath", "VC_LibraryPath_x64", "WindowsSDK_IncludePath",
             "WindowsSDK_LibraryPath_x64", "NETFXKitsDir", "VC_ExecutablePath_x64")
foreach ($var in $envVars) {
    $val = [Environment]::GetEnvironmentVariable($var, "Process")
    if ($val) {
        Write-Ok "$var = $val"
    } else {
        Write-Info "$var не задана (нормально вне dev-командной строки)"
    }
}

Write-Host ""

# ── Summary ────────────────────────────────────────────
Write-Host "=== Итог ===" -ForegroundColor Cyan
if ($foundIssues.Count -eq 0) {
    Write-Host "Проблем не обнаружено." -ForegroundColor Green
} else {
    if ($foundIssues.Count -le 2) {
        Write-Host "Найдено несоответствий: $($foundIssues.Count)" -ForegroundColor Yellow
        foreach ($issue in $foundIssues) {
            Write-Host "  - $issue" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "Подсказка: запустите Visual Studio Installer и проверьте компонент" -ForegroundColor Cyan
        Write-Host "'Desktop development with C++' (или выполните ameni vs vsconfig)." -ForegroundColor Cyan
    } else {
        Write-Host "Найдено несоответствий: $($foundIssues.Count)" -ForegroundColor Red
        foreach ($issue in $foundIssues) {
            Write-Host "  - $issue" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Рекомендация: запустите Visual Studio Installer и убедитесь, что компоненты" -ForegroundColor Yellow
        Write-Host "'Desktop development with C++' и Windows SDK установлены." -ForegroundColor Yellow
    }
}
