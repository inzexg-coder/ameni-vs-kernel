# Visual Studio 2017 (v141) — VC++ Directories

| Свойство | Значение |
|---|---|
| Executable Directories | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |
| Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| Library Directories | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |

## Особенности VS 2017

- MSVC toolchain по умолчанию: `C:\Program Files (x86)\Microsoft Visual Studio\2017\*\VC\Tools\MSVC\14.1*\lib\x64`
- `$(NETFXKitsDir)` указывает на `C:\Program Files (x86)\Windows Kits\10\`
- Аналогичен VS 2022, но пути могут отличаться мажорной версией MSVC.
