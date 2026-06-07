# Visual Studio 2025 (v144) — VC++ Directories

Актуальные пути для VS 2025 (v144).

| Свойство | Значение |
|---|---|
| Executable Directories | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |
| Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| Library Directories | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |

## Особенности VS 2025

- MSVC toolchain: `...\Microsoft Visual Studio\2025\*\VC\Tools\MSVC\14.4*\lib\x64`
- Если используется Windows SDK 11.0, путь к `kernel32.lib`:
  `$(NETFXKitsDir)Lib\um\x64` может указывать на `Windows Kits\11\lib\<version>\um\x64`
- Рекомендуется проверить `$(NETFXKitsDir)` через `verify-environment.ps1`
