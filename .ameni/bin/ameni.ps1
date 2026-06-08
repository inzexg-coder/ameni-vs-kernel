<#
.SYNOPSIS
  Ameni VS Kernel - cross-platform Visual Studio diagnostic agent.
  Works on Windows (PowerShell), Arch Linux (bash), and macOS.

.DESCRIPTION
  Commands:
    diagnose         Full environment diagnostics
    check [path]     Inspect .vcxproj files
    props            List available property sheets
    errors [name]    Linker error reference
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
  Write-Host "OS: $([Environment]::OSVersion.VersionString) ($([Environment]::Is64BitOperatingSystem ? 'x64' : 'x86'))"
  Write-Host ""

  $psScript = "$ScriptsDir/verify-environment.ps1"
  if (Test-Path $psScript) {
    & $psScript
  }
  else {
    Write-Host "[INFO]  Running standalone diagnostics" -ForegroundColor Green
    # Check dotnet
    $dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
    if ($dotnet) {
      $dv = & dotnet --version
      Write-Host "[INFO]  dotnet SDK: $dv" -ForegroundColor Green
    } else {
      Write-Host "[WARN]  dotnet not found in PATH" -ForegroundColor Yellow
    }
    # Check pwsh
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
    foreach ($f in $projFiles) {
      Write-Host "    $($f.Name)"
    }
    Write-Host ""
    Write-Host "[INFO]  Run diff-project-settings.ps1 for detailed comparison:" -ForegroundColor Green
    Write-Host "    pwsh $ScriptsDir/diff-project-settings.ps1 -ProjectPath `"$($projFiles[0].FullName)`""
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
      if ($content -match '<\w+>(.*)</\w+>') {
        Write-Host "  -  $($matches[1])" -ForegroundColor Gray
      } else { Write-Host "" }
    }
  } else {
    Write-Host "[WARN]  props/ directory not found" -ForegroundColor Yellow
  }
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
    foreach ($e in $errors) {
      $name = $e.BaseName
      $desc = (Get-Content $e.FullName -TotalCount 1 -ErrorAction SilentlyContinue) -replace '# ',''
      Write-Host ("  {0,-35} {1}" -f $name, ($desc -join ''))
    }
    Write-Host ""
    Write-Host "Usage: ameni vs errors <error-name>"
  }
}

function Cmd-About {
  Write-Host ""
  Write-Host "Ameni VS Kernel"
  Write-Host "Visual Studio Configuration Archive & Diagnostic Agent"
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
  Write-Host "  ameni vs errors lnk1104-cannot-open-file"
  Write-Host ""
  Write-Host "REFERENCE"
  Write-Host "  https://github.com/inzexg-coder/ameni-vs-kernel"
  Write-Host ""
}

switch ($Command) {
  "diagnose"  { Cmd-Diagnose }
  "check"     { Cmd-Check $Argument }
  "props"     { Cmd-Props }
  "errors"    { Cmd-Errors $Argument }
  "about"     { Cmd-About }
  "help"      { Cmd-Help }
  default     { Cmd-Help }
}
