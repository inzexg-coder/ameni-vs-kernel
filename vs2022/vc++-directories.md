# Visual Studio 2022 (v143) — VC++ Directories

Полностью соответствует основному `vc++-directories.md` в корне репозитория.
Дублируется здесь для удобства навигации по версиям.

| Свойство | Значение |
|---|---|
| Executable Directories | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |
| Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| External Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| Reference Directories | `$(VC_ReferencesPath_x64);` |
| Library Directories | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |
| Library WinRT Directories | `$(WindowsSDK_MetadataPath);` |
| Source Directories | `$(VC_SourcePath);` |
| Exclude Directories | `$(VC_SourcePath);` |
