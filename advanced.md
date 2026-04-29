## Detailed Configuration Reference

The following properties represent the non-default or otherwise critical settings archived within this repository. These values have been verified to produce a stable build environment when combined with the default directory paths referenced earlier. Adherence to these settings is recommended when restoring linker behavior, particularly for `kernel32.lib` resolution.

### Advanced Properties

| Property | Value |
|----------|-------|
| Target File Extension | `.exe` |
| Extensions to Delete on Clean | `*.cdf;*.cache;*.obj;*.obj.enc;*.ilk;*.ipdb;*.iobj;*.resources;*.tlb;*.tli;*.tlh;*.tmp;*.rsp;*.pgc;*.pgd;*.meta;*.tlog;*.manifest;*.res;*.pch;*.exp;*.idb;*.rep;*.xdc;*.pdb;*_manifest.rc;*.bsc;*.sbr;*.xml;*.metagen;*.bi` |
| Build Log File | `$(IntDir)$(MSBuildProjectName).log` |
| Preferred Build Tool Architecture | `Default` |
| Use Debug Libraries | `Yes` |
| Enable Unity (JUMBO) Build | `No` |
| Copy Content to OutDir | `No` |
| Copy Project References to OutDir | `No` |
| Copy Project References' Symbols to OutDir | `No` |
| Copy C++ Runtime to OutDir | `No` |
| Use of MFC | `Use Standard Windows Libraries` |
| Character Set | `Use Unicode Character Set` |
| Whole Program Optimization | `No Whole Program Optimization` |
| MSVC Toolset Version | `Default` |
| Enable MSVC Structured Output | `Yes` |

### C++/CLI Properties

| Property | Value |
|----------|-------|
| Common Language Runtime Support | `No Common Language Runtime Support` |
| .NET Target Framework Version | (empty) |
| Enable Managed Incremental Build | `No` |
| Enable CLR Support for Individual Files | (empty) |

## Interpretation for Troubleshooting

- **Use Debug Libraries set to `Yes`** ensures that debug versions of runtime libraries are linked when building debug configurations. This setting is compatible with standard `kernel32.lib` resolution and does not alter system library search paths.
- **No Common Language Runtime Support** indicates that the project is native C++ and does not host the .NET runtime. Consequently, `kernel32.lib` linkage depends exclusively on the Windows SDK and VC++ library directories.
- **Empty values** for .NET Target Framework and per‑file CLR support explicitly disable managed code features, reducing potential conflicts with native linker settings.

## Application to Kernel32.lib Issues

If `kernel32.lib` errors persist after restoring the default directory paths described in the main section of this documentation, verify that the Advanced and C++/CLI properties listed above match your project settings. Deviations such as enabling Whole Program Optimization or altering the Character Set can modify the linker’s import library selection. Restoring the archived configuration eliminates these variables and returns the build environment to a known working state.
