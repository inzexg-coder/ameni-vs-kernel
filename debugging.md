### Debugger Settings

The following debugger configuration is archived as part of the standard project environment. These settings ensure that execution begins from the correct working directory and that the default debugging engine behaves predictably. Restoring these values is recommended when troubleshooting runtime misbehavior that may be mistaken for linker or library errors such as those involving `kernel32.lib`.

| Property | Value |
|----------|-------|
| Command | `$(TargetPath)` |
| Command Arguments | (empty) |
| Working Directory | `$(ProjectDir)` |
| Attach | `No` |
| Debugger Type | `Auto` |
| Environment | (empty) |
| Merge Environment | `Yes` |
| SQL Debugging | `No` |
| AMP Default Accelerator | `WARP software accelerator` |

## Interpretation for Troubleshooting

- **Command set to `$(TargetPath)`** directs the debugger to launch the exact executable produced by the build. No intermediate or custom launcher is used, eliminating an additional variable when diagnosing linker failures.

- **Working Directory set to `$(ProjectDir)`** ensures that relative paths used by the executable resolve to the project source directory rather than the output directory. This is particularly relevant for applications that load configuration files or assets at startup; misconfigured working directories can produce runtime errors that may be incorrectly attributed to missing libraries.

- **Attach set to `No`** means the debugger starts a new process instance rather than attaching to an existing one. This is the standard behavior for most native C++ projects and avoids complications related to process injection or insufficient permissions.

- **Debugger Type set to `Auto`** allows Visual Studio to select the appropriate debugging engine (native, managed, or mixed) based on the executable content. For native projects that do not use the common language runtime, this correctly defaults to the native debugger.

- **Environment left empty and Merge Environment set to `Yes`** instructs the debugger to inherit the system environment variables rather than overriding them. This preserves standard system paths, including those that may affect library loading behavior.

- **AMP Default Accelerator set to `WARP software accelerator`** configures the C++ AMP runtime to use the software fallback (WARP) rather than attempting to initialize a hardware GPU. This setting does not directly affect `kernel32.lib` resolution, but enforcing a consistent accelerator avoids runtime initialization failures that could be misinterpreted as build or linkage problems.

## Application to Kernel32.lib and Related Issues

While debugger settings do not directly resolve static linking errors such as unresolved `kernel32.lib` symbols, they are archived here to provide a complete, reproducible environment. In complex troubleshooting scenarios, mismatched debugger configurations can produce runtime errors that obscure the underlying linker problem. By restoring the debugger settings shown above, developers eliminate one class of runtime misconfiguration and can focus on verifying directory paths and library dependencies as described in the main section of this documentation.

If `kernel32.lib` errors disappear when running outside the debugger but reappear when debugging, confirm that the working directory and environment settings match this archived configuration. Otherwise, refer to the Advanced and C++/CLI properties documented earlier for complete restoration steps.
