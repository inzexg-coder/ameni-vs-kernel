<#
.SYNOPSIS
  Ameni VS Kernel - cross-platform Visual Studio diagnostic agent.
  Works on Windows (PowerShell), Arch Linux (bash), and macOS.

.DESCRIPTION
  Commands:
    diagnose         Full environment diagnostics
    check [path]     Inspect .vcxproj files
    fix [path]       Auto-fix LibraryDirectories in .vcxproj (creates .bak)
    props            List available property sheets
    errors [name]    Linker error reference
    vsconfig         Import .vsconfig via VS Installer CLI
    about            Display agent information
    help             Show detailed help
#>

param(
  [string]$Command = "help",
  [string]$Argument = ""
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path "$ScriptDir/../.."
$ScriptsDir = "$RepoRoot/scripts"

function Cmd-Diagnose {
  Write-Host "=== Environment Diagnostics ===" -ForegroundColor Cyan
  $osInfo = [Environment]::OSVersion.VersionString
  if ([Environment]::Is64BitOperatingSystem) {
    $arch = "x64"
  } else {
    $arch = "x86"
  }
  Write-Host "OS: $osInfo ($arch)"
  Write-Host ""

  $psScript = "$ScriptsDir/verify-environment.ps1"
  if (Test-Path $psScript) {
    & $psScript
  } else {
    Write-Host "[INFO]  Running standalone diagnostics" -ForegroundColor Green
    $dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
    if ($dotnet) {
      $dv = & dotnet --version
      Write-Host "[INFO]  dotnet SDK: $dv" -ForegroundColor Green
    } else {
      Write-Host "[WARN]  dotnet not found in PATH" -ForegroundColor Yellow
    }
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwsh) {
      Write-Host "[INFO]  PowerShell Core: $($pwsh.Source)" -ForegroundColor Green
    } else {
      Write-Host "[WARN]  pwsh not found. Using Windows PowerShell." -ForegroundColor Yellow
    }
  }
}

function Cmd-Check {
  param([string]$Path = ".")
  if (-not (Test-Path $Path -PathType Container)) {
    Write-Host "[ERROR] Directory not found: $Path" -ForegroundColor Red
    exit 1
  }
  $Path = Resolve-Path $Path
  Write-Host "=== Project Structure Check ===" -ForegroundColor Cyan
  Write-Host "Path: $Path"
  Write-Host ""

  $projFiles = Get-ChildItem -Path $Path -Filter "*.vcxproj" -Recurse -ErrorAction SilentlyContinue
  if ($projFiles.Count -gt 0) {
    Write-Host "[INFO]  Found .vcxproj files:" -ForegroundColor Green
    $mismatches = 0
    foreach ($f in $projFiles) {
      Write-Host "    $($f.Name)"
      $diffScript = "$ScriptsDir/diff-project-settings.ps1"
      if (Test-Path $diffScript) {
        $result = & $diffScript -ProjectPath $f.FullName 2>&1
        if ($result -match '\[!\]' -or $result -match 'расхождений') {
          $mismatches++
        }
      }
    }
    Write-Host ""
    if ($mismatches -gt 0) {
      Write-Host "[!]  LibraryDirectories non-standard - use 'ameni vs fix'" -ForegroundColor Yellow
    } else {
      Write-Host "[OK]  All settings match reference." -ForegroundColor Green
    }
  } else {
    Write-Host "[WARN]  No .vcxproj files found in $Path" -ForegroundColor Yellow
  }
}

function Cmd-Props {
  Write-Host "=== Available Property Sheets ===" -ForegroundColor Cyan
  Write-Host ""
  $propsDir = "$RepoRoot/props"
  if (Test-Path $propsDir) {
    $props = Get-ChildItem -Path $propsDir -Filter "*.props"
    foreach ($p in $props) {
      $name = $p.BaseName
      $content = Get-Content $p.FullName -TotalCount 1 -ErrorAction SilentlyContinue
      Write-Host "  $name" -NoNewline
      if ($content -match "<(\w+)>(.*)</\1>") {
        Write-Host "  -  $($matches[1])" -ForegroundColor Gray
      } else {
        Write-Host ""
      }
    }
  } else {
    Write-Host "[WARN]  props/ directory not found" -ForegroundColor Yellow
  }
}

function Cmd-Fix {
  param([string]$Path = ".", [string]$Arch = "x64")
  if (-not (Test-Path $Path)) {
    Write-Host "[ERROR] Path not found: $Path" -ForegroundColor Red
    exit 1
  }
  $Path = Resolve-Path $Path
  Write-Host "=== Auto-fix .vcxproj paths ===" -ForegroundColor Cyan
  Write-Host "Path: $Path"
  Write-Host "Architecture: $Arch"
  Write-Host ""

  $fixScript = "$ScriptsDir/apply-default-paths.ps1"
  if (Test-Path $fixScript) {
    & $fixScript -Path $Path -Architecture $Arch
  } else {
    Write-Host "[ERROR] Script not found: $fixScript" -ForegroundColor Red
    exit 1
  }
}

function Cmd-VsConfig {
  Write-Host "=== Import .vsconfig via VS Installer CLI ===" -ForegroundColor Cyan
  Write-Host ""

  $vsconfigPath = "$RepoRoot/.vsconfig"
  if (-not (Test-Path $vsconfigPath)) {
    Write-Host "[ERROR] .vsconfig not found at $vsconfigPath" -ForegroundColor Red
    exit 1
  }

  $vswherePaths = @(
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe",
    "${env:ProgramFiles}\Microsoft Visual Studio\Installer\vswhere.exe"
  )
  $vswherePath = $null
  foreach ($p in $vswherePaths) {
    if (Test-Path $p) { $vswherePath = $p; break }
  }

  if (-not $vswherePath) {
    Write-Host "[ERROR] vswhere.exe not found. Visual Studio may not be installed." -ForegroundColor Red
    exit 1
  }

  Write-Host "[OK] vswhere.exe found" -ForegroundColor Green
  $vswhereOutput = & $vswherePath -products * -format json 2>$null
  if (-not $vswhereOutput) {
    Write-Host "[ERROR] vswhere returned empty result. Visual Studio not installed?" -ForegroundColor Red
    exit 1
  }
  try {
    $vsInfo = $vswhereOutput | ConvertFrom-Json -ErrorAction Stop
  } catch {
    Write-Host "[ERROR] Could not parse vswhere output: $_" -ForegroundColor Red
    exit 1
  }
  if (-not $vsInfo) {
    Write-Host "[ERROR] No Visual Studio installations found." -ForegroundColor Red
    exit 1
  }

  $installer = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vs_installer.exe"
  if (-not (Test-Path $installer)) {
    Write-Host "[ERROR] vs_installer.exe not found at $installer" -ForegroundColor Red
    exit 1
  }

  foreach ($vs in $vsInfo) {
    $installPath = $vs.installationPath
    $displayName = $vs.displayName
    Write-Host "  Found: $displayName at $installPath" -ForegroundColor Gray
    Write-Host "  Running: vs_installer.exe modify --installPath `"$installPath`" --configFile `"$vsconfigPath`"" -ForegroundColor Cyan
    Write-Host "  Starting installation (this may take a while)..." -ForegroundColor Yellow
    & $installer modify --installPath $installPath --configFile $vsconfigPath --quiet --norestart
    Write-Host "  [OK] Done for $displayName" -ForegroundColor Green
  }
  Write-Host ""
  Write-Host "Done. Restart Visual Studio if needed." -ForegroundColor Green
}

function Cmd-Errors {
  param([string]$ErrorName = "")
  Write-Host "=== Linker Error Reference ===" -ForegroundColor Cyan
  Write-Host ""
  $errorsDir = "$RepoRoot/errors"
  if ($ErrorName) {
    $file = "$errorsDir/$ErrorName.md"
    if (Test-Path $file) {
      Get-Content $file
    } else {
      Write-Host "[ERROR] Reference not found: $ErrorName" -ForegroundColor Red
    }
  } else {
    $errors = Get-ChildItem -Path $errorsDir -Filter "*.md" -ErrorAction SilentlyContinue
    if ($errors) {
      foreach ($e in $errors) {
        $name = $e.BaseName
        $desc = (Get-Content $e.FullName -TotalCount 1 -ErrorAction SilentlyContinue) -replace '# ',''
        Write-Host ("  {0,-35} {1}" -f $name, ($desc -join ''))
      }
    }
    Write-Host ""
    Write-Host "Usage: ameni vs errors [error-name]"
  }
}

function Cmd-About {
  Write-Host ""
  Write-Host "Ameni VS Kernel"
  $aboutLine = "Visual Studio Configuration Archive and Diagnostic Agent"
  Write-Host $aboutLine
  Write-Host "https://github.com/inzexg-coder/ameni-vs-kernel"
  Write-Host ""
  Write-Host "Platforms: Windows, Arch Linux, macOS"
  Write-Host ""
  Write-Host "Commands:"
  Write-Host "  diagnose         Full environment diagnostics"
  Write-Host "  check [path]     Inspect .vcxproj files"
  Write-Host "  props            List available property sheets"
  Write-Host "  errors [name]    Linker error reference"
  Write-Host "  about            Display this information"
  Write-Host "  help             Show detailed help"
  Write-Host ""
}

function Cmd-Help {
  Write-Host ""
  Write-Host "NAME"
  Write-Host "  ameni vs - Visual Studio build diagnostic agent (cross-platform)"
  Write-Host ""
  Write-Host "SYNOPSIS"
  Write-Host "  ameni vs diagnose"
  Write-Host "  ameni vs check [path]"
  Write-Host "  ameni vs props"
  Write-Host "  ameni vs errors [name]"
  Write-Host ""
  Write-Host "DESCRIPTION"
  Write-Host "  Cross-platform diagnostic toolkit for Visual Studio build"
  Write-Host "  configuration. All commands run on Windows, Arch Linux, and macOS."
  Write-Host ""
  Write-Host "EXAMPLES"
  Write-Host "  ameni vs diagnose"
  Write-Host "  ameni vs check /path/to/project"
  Write-Host "  ameni vs fix /path/to/project -arch x64"
  Write-Host "  ameni vs vsconfig"
  Write-Host "  ameni vs errors lnk1104-cannot-open-file"
  Write-Host ""
  Write-Host "REFERENCE"
  Write-Host "  https://github.com/inzexg-coder/ameni-vs-kernel"
  Write-Host ""
}

switch ($Command) {
  "diagnose" {
    Cmd-Diagnose
  }
  "check" {
    if ($Argument) {
      Cmd-Check $Argument
    } else {
      Cmd-Check
    }
  }
  "fix" {
    $fixPath = "."
    if ($Argument) {
      $fixPath = $Argument
    }
    $fixArch = "x64"
    if ($args.Count -gt 0) {
      $fixArch = $args[0]
    }
    Cmd-Fix $fixPath $fixArch
  }
  "props" {
    Cmd-Props
  }
  "errors" {
    Cmd-Errors $Argument
  }
  "vsconfig" {
    Cmd-VsConfig
  }
  "about" {
    Cmd-About
  }
  "help" {
    Cmd-Help
  }
  default {
    Cmd-Help
  }
}
