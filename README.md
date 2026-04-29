# Visual Studio Configuration Archive

This repository serves as a structured archive of text-based configuration files containing predefined path settings for Visual Studio projects. Its primary purpose is to provide a recoverable baseline of environment settings that can be reapplied in cases where build configurations become corrupted or misaligned.

## Scope and Intended Use

The repository stores plain-text representations of include directories, library directories, and linker dependencies as they appear in a standard Visual Studio installation. These files are organized to allow rapid restoration of default project configurations without requiring a full reinstallation of the development environment or manual reconstruction of settings through the IDE interface.

## Addressing Kernel32.lib and Related Linker Issues

A known failure pattern in Visual Studio builds involves unresolved external symbols originating from the Windows SDK, most commonly manifesting as errors referencing `kernel32.lib`. These errors typically indicate that the linker is unable to locate core system libraries due to altered or missing default search paths.

In such situations, the most reliable resolution is to reset all Visual Studio directory settings to their factory defaults. This repository provides the exact reference paths and configuration structures against which a working baseline is defined. By comparing or replacing the current project and solution settings with those archived here, the standard search order for `kernel32.lib` and other foundational libraries can be fully restored.

## Recommended Workflow

1.  Verify that the Windows SDK and Visual Studio build tools are installed and properly registered.
2.  Open the affected project or solution and navigate to its property pages.
3.  Review the `VC++ Directories` and `Linker > General` sections.
4.  Cross-reference the configured paths with the defaults documented in this repository.
5.  Replace any deviant entries with the default paths as shown in the archived configuration files.
6.  Rebuild the project to confirm resolution of the `kernel32.lib` or related linker errors.

## Scope of Support

This repository does not provide binary libraries or installers. It offers only declarative, human-readable configuration templates intended for developers familiar with Visual Studio project management. These files are provided as reference material and should be adapted to the specific version of Visual Studio and Windows SDK in use.

For persistent issues beyond path configuration, consult the official Visual Studio or Windows SDK documentation.
