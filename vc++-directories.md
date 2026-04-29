### VC++ Directories

The following VC++ Directory settings define the search paths used by the compiler and linker during build operations. These paths are the most critical component for resolving `kernel32.lib` and other system dependencies. The values archived in this repository represent the default, unaltered configuration as established by a clean installation of Visual Studio 2022 with the Windows 10 SDK.

## General (VC++ Directories)

| Property | Value |
|----------|-------|
| Executable Directories | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |
| Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| External Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| Reference Directories | `$(VC_ReferencesPath_x64);` |
| Library Directories | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |
| Library WinRT Directories | `$(WindowsSDK_MetadataPath);` |
| Source Directories | `$(VC_SourcePath);` |
| Exclude Directories | `$(VC_SourcePath);` |

## Public Project Content

| Property | Value |
|----------|-------|
| Public Include Directories | (empty) |
| All Header Files are Public | `No` |
| Public C++ Module Directories | (empty) |
| All Modules are Public | `No` |

## Interpretation for Troubleshooting

### Executable Directories
Set to `$(VC_ExecutablePath_x64);$(CommonExecutablePath)`. These paths contain the compiler (cl.exe), linker (link.exe), and other build tools. If these directories are missing or overridden, the build may fail to invoke the correct toolchain. Restoring this default ensures that the expected version of link.exe is used.

### Include Directories
Set to `$(VC_IncludePath);$(WindowsSDK_IncludePath);`. The trailing semicolon is preserved as in the original configuration. These paths contain C++ standard library headers and Windows SDK headers. Deviations from this order can cause incorrect macro definitions or mismatched type declarations, which rarely affect linking but are included for completeness.

### External Include Directories
Identical to Include Directories. This property applies to external header files treated as system headers. The archived value suppresses warnings from Windows SDK headers when external warning levels are enabled.

### Reference Directories
Set to `$(VC_ReferencesPath_x64);`. Used for WinRT and .NET reference assemblies. Not relevant to native `kernel32.lib` linking, but included to maintain a complete archived state.

### Library Directories
**This property is the primary location for `kernel32.lib` resolution.** The archived value is:
`$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64`

- `$(VC_LibraryPath_x64)` resolves to the Visual Studio C++ runtime library directory (e.g., `...\VC\Tools\MSVC\<version>\lib\x64`). Contains libvcruntime, libcmt, and other compiler-support libraries.
- `$(WindowsSDK_LibraryPath_x64)` resolves to the Windows SDK library directory (e.g., `...\Windows Kits\10\lib\<version>\ucrt\x64`). Contains the Universal CRT import libraries.
- `$(NETFXKitsDir)Lib\um\x64` resolves to the Windows SDK User Mode library directory (e.g., `...\Windows Kits\10\lib\<version>\um\x64`). **This path contains `kernel32.lib`.**

If `kernel32.lib` is not found, verify the following:
1. `$(NETFXKitsDir)` is defined correctly. This macro typically expands to `C:\Program Files (x86)\Windows Kits\10\`.
2. The Windows SDK is installed and includes the `um\x64` subdirectory.
3. No additional paths have been inserted before the default entries that might redirect the linker to an incorrect or older version of `kernel32.lib`.

### Library WinRT Directories
Set to `$(WindowsSDK_MetadataPath);`. Used for WinRT component resolution. Does not affect `kernel32.lib`.

### Source Directories
Set to `$(VC_SourcePath);`. Contains source files for C++ standard library implementations. Not relevant to linking.

### Exclude Directories
Set to `$(VC_SourcePath);`. Specifies paths that the build system should ignore during scanning operations. Not relevant to linking.

## Public Project Content Notes

All properties in this section are either empty or set to default values that do not expose internal headers as public interfaces. These settings have no effect on `kernel32.lib` resolution and are archived solely for completeness of the project state.

## Application to Kernel32.lib Issues

When encountering unresolved external symbols related to `kernel32.lib` (e.g., `WinMain`, `CreateFile`, `CloseHandle`), the most direct resolution is to restore the **Library Directories** property exactly as shown above. This property must contain the `$(NETFXKitsDir)Lib\um\x64` path before any custom or third-party library directories that might shadow or omit the required import library.

To restore the configuration:

1. Open the project Property Pages.
2. Navigate to **Configuration Properties > VC++ Directories**.
3. For **Library Directories**, select the dropdown and choose `<Edit...>`.
4. Replace the existing value with:
   `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64`
5. Ensure there are no leading or trailing spaces unless intentionally preserved.
6. Click OK and rebuild the project.

If `kernel32.lib` errors persist after restoring the Library Directories, verify that the following paths exist on the build machine:

- `$(NETFXKitsDir)Lib\um\x64\kernel32.lib`
- `$(WindowsSDK_LibraryPath_x64)\ucrt.lib`
- `$(VC_LibraryPath_x64)\vcruntime.lib`

The absence of any of these files indicates an incomplete or corrupted Visual Studio or Windows SDK installation. Reinstalling the Windows SDK or repairing Visual Studio through the Visual Studio Installer will restore missing libraries.

This repository provides these VC++ Directory settings as the definitive reference for resolving library search path issues. All other archived properties (General, Advanced, Debugger, C++/CLI) support this configuration but do not replace the necessity of correct Library Directories.
