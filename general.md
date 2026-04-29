### General Properties

The following General properties define the fundamental output locations, naming conventions, and platform tooling for projects archived in this repository. These settings are part of the baseline configuration that, when combined with the default directory paths described previously, ensures correct resolution of system libraries including `kernel32.lib`.

| Property | Value |
|----------|-------|
| Output Directory | `$(SolutionDir)$(Platform)\$(Configuration)\` |
| Intermediate Directory | `$(ShortProjectName)\$(Platform)\$(Configuration)\` |
| Target Name | `$(ProjectName)` |

### Examples

The following table provides representative values for a typical Windows desktop application. These examples illustrate how the archived configuration should appear in a standard Visual Studio project.

| Property | Value |
|----------|-------|
| Configuration Type | `Application (.exe)` |
| Windows SDK Version | `10.0 (latest installed version)` |
| Platform Toolset | `Visual Studio 2022 (v143)` |
| C++ Language Standard | `Default (ISO C++14 Standard)` |
| C Language Standard | `Default (Legacy MSVC)` |

## Interpretation for Troubleshooting

- **Output Directory** is set to a solution-relative path organized by platform and configuration. This keeps build artifacts separate from source files and ensures that linker outputs, including the final `.exe` file, are placed in a predictable location. When `kernel32.lib` linkage fails, confirming that the output directory is writable and does not contain stale object files from a previous configuration is a recommended diagnostic step.

- **Intermediate Directory** uses `$(ShortProjectName)` as a root to avoid path length limitations and collision between projects. Object files (`.obj`), program databases (`.pdb`), and build logs are written to this location. Cleaning or deleting this directory forces a full rebuild, which can resolve residual linker errors caused by mismatched COMDAT records or corrupted import libraries.

- **Target Name** defaults to `$(ProjectName)`, producing an executable with the same base name as the project file. This behavior is standard and does not interfere with library resolution.

## Configuration Type and Toolset Notes

- **Configuration Type set to `Application (.exe)`** instructs the build system to produce a portable executable for the Windows operating system. The linker expects to resolve `kernel32.lib` and other system libraries when generating an `.exe` target. Projects archived with this setting rely on the default SDK and toolset paths.

- **Windows SDK Version set to `10.0 (latest installed version)`** means the build targets the most recent Windows 10 SDK available on the local machine. This is critical for `kernel32.lib` resolution, as the SDK provides the import library that maps Windows API calls to their system implementations. If the specified SDK version is not installed, the build fails with unresolved externals. Restoring the archived configuration requires ensuring that at least one Windows 10 SDK version is present.

- **Platform Toolset set to `Visual Studio 2022 (v143)`** indicates that the project is intended for use with Visual Studio 2022. Older toolsets may rely on different directory layouts or library distributions. When encountering `kernel32.lib` errors, verify that the installed toolset matches this archived setting or update the project to use an available toolset while keeping all other paths as documented.

- **C++ Language Standard set to `Default (ISO C++14 Standard)`** and **C Language Standard set to `Default (Legacy MSVC)`** represent conservative language conformance settings. These do not affect linker behavior or SDK path resolution. They are included in the archive to provide a complete, reproducible environment.

## Application to Kernel32.lib Issues

If `kernel32.lib` remains unresolved after restoring all previously documented settings (directory paths, advanced properties, debugger configuration, and general properties), perform the following verification steps:

1. Confirm that the Windows SDK selected in the project is actually installed. The value `10.0 (latest installed version)` automatically resolves to an existing SDK, but manual selection of a specific version number may fail if that version is absent.

2. Verify that the Platform Toolset is compatible with the installed Visual Studio version. A mismatch between the archived toolset (v143) and the available toolsets will prevent the build system from locating required libraries.

3. Clean the Intermediate Directory and rebuild the project. Residual object files from previous builds can cause inconsistent linking even when directory paths are correct.

4. Ensure that the Output Directory is not redirected to a network location or a path containing special characters that might interfere with the linker.

This repository provides these General properties as part of a complete, recoverable baseline. Reapplying all settings from the archive — including directory paths, advanced options, debugger configuration, and general properties — offers the highest probability of resolving `kernel32.lib` and related linker errors.
