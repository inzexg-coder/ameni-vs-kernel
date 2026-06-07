

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath
)

if (-not (Test-Path $ProjectPath)) {
    Write-Host "Файл не найден: $ProjectPath" -ForegroundColor Red
    exit 1
}

$referencePaths = @{
    "ExecutableDirectories" = '$(VC_ExecutablePath_x64);$(CommonExecutablePath)'
    "IncludeDirectories" = '$(VC_IncludePath);$(WindowsSDK_IncludePath);'
    "ExternalIncludeDirectories" = '$(VC_IncludePath);$(WindowsSDK_IncludePath);'
    "ReferenceDirectories" = '$(VC_ReferencesPath_x64);'
    "LibraryDirectories" = '$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64'
    "LibraryWinRTDirectories" = '$(WindowsSDK_MetadataPath);'
    "SourceDirectories" = '$(VC_SourcePath);'
    "ExcludeDirectories" = '$(VC_SourcePath);'
}

Write-Host "=== Diff: проект vs эталон ===" -ForegroundColor Cyan
Write-Host "Файл: $ProjectPath" -ForegroundColor Gray
Write-Host ""

$xml = [xml](Get-Content $ProjectPath -Raw)
$ns = @{ ns = "http://schemas.microsoft.com/developer/msbuild/2003" }
$mismatches = 0

foreach ($prop in $referencePaths.Keys) {
    $xpath = "//ns:PropertyGroup/ns:$prop"
    $node = $xml.SelectSingleNode($xpath, $ns)

    if ($node -and $node.InnerText) {
        $current = $node.InnerText.Trim()
        $expected = $referencePaths[$prop]

        if ($current -ne $expected) {
            Write-Host "  [!] $prop" -ForegroundColor Yellow
            Write-Host "      Сейчас:   $current" -ForegroundColor Red
            Write-Host "      Эталон:  $expected" -ForegroundColor Green
            $mismatches++
        } else {
            Write-Host "  [OK] $prop" -ForegroundColor Green
        }
    } else {
        Write-Host "  [--] $prop не найдена в проекте" -ForegroundColor Gray
    }
}

Write-Host ""
if ($mismatches -eq 0) {
    Write-Host "Все настройки совпадают с эталоном." -ForegroundColor Green
} else {
    Write-Host "Найдено расхождений: $mismatches" -ForegroundColor Yellow
    Write-Host "Используйте apply-default-paths.ps1 для автоматического исправления." -ForegroundColor Cyan
}
