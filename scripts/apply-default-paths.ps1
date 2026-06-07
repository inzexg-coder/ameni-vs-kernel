

param(
    [string]$Path = ".",
    [ValidateSet("x64", "x86", "ARM64")]
    [string]$Architecture = "x64",
    [bool]$Backup = $true
)

$libraryDirs = @{
    "x64"   = '$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64'
    "x86"   = '$(VC_LibraryPath_x86);$(WindowsSDK_LibraryPath_x86);$(NETFXKitsDir)Lib\um\x86'
    "ARM64" = '$(VC_LibraryPath_ARM64);$(WindowsSDK_LibraryPath_ARM64);$(NETFXKitsDir)Lib\um\arm64'
}

$includeDirs = '$(VC_IncludePath);$(WindowsSDK_IncludePath);'
$execDirs = @{
    "x64"   = '$(VC_ExecutablePath_x64);$(CommonExecutablePath)'
    "x86"   = '$(VC_ExecutablePath_x86);$(CommonExecutablePath)'
    "ARM64" = '$(VC_ExecutablePath_ARM64);$(CommonExecutablePath)'
}

$projFiles = Get-ChildItem -Path $Path -Filter "*.vcxproj" -Recurse

if ($projFiles.Count -eq 0) {
    Write-Host "Файлы .vcxproj не найдены в $Path" -ForegroundColor Yellow
    exit 1
}

Write-Host "Найдено проектов: $($projFiles.Count)" -ForegroundColor Cyan

foreach ($proj in $projFiles) {
    Write-Host "Обработка: $($proj.Name)" -ForegroundColor Gray
    $content = Get-Content $proj.FullName -Raw

    if ($Backup) {
        $backupPath = "$($proj.FullName).bak"
        Copy-Item $proj.FullName $backupPath -Force
        Write-Host "  -> Бэкап: $backupPath" -ForegroundColor Gray
    }

        if ($content -match '<LibraryDirectories>[^<]*</LibraryDirectories>') {
        $content = $content -replace '<LibraryDirectories>[^<]*</LibraryDirectories>',
            "<LibraryDirectories>$($libraryDirs[$Architecture])</LibraryDirectories>"
        Write-Host "  [OK] LibraryDirectories -> $($libraryDirs[$Architecture])" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] LibraryDirectories не найдена в XML" -ForegroundColor Yellow
    }

        if ($content -match '<IncludeDirectories>[^<]*</IncludeDirectories>') {
        $content = $content -replace '<IncludeDirectories>[^<]*</IncludeDirectories>',
            "<IncludeDirectories>$includeDirs</IncludeDirectories>"
        Write-Host "  [OK] IncludeDirectories -> эталон" -ForegroundColor Green
    }

        if ($content -match '<ExecutableDirectories>[^<]*</ExecutableDirectories>') {
        $content = $content -replace '<ExecutableDirectories>[^<]*</ExecutableDirectories>',
            "<ExecutableDirectories>$($execDirs[$Architecture])</ExecutableDirectories>"
        Write-Host "  [OK] ExecutableDirectories -> эталон" -ForegroundColor Green
    }

    Set-Content $proj.FullName $content -NoNewline
}

Write-Host ""
Write-Host "Готово! Пути обновлены для архитектуры $Architecture." -ForegroundColor Green
Write-Host "Для отката используйте .bak файлы." -ForegroundColor Gray
