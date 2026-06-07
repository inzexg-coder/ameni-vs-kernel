# Visual Studio Configuration Archive

This repository serves as a structured archive of text-based configuration files containing predefined path settings for Visual Studio projects. Its primary purpose is to provide a recoverable baseline of environment settings that can be reapplied in cases where build configurations become corrupted or misaligned.

## Scope and Intended Use

The repository stores plain-text representations of include directories, library directories, and linker dependencies as they appear in a standard Visual Studio installation. These files are organized to allow rapid restoration of default project configurations without requiring a full reinstallation of the development environment or manual reconstruction of settings through the IDE interface.

## Repository Structure

```
visual-studio-fixing/
├── props/                    # Property sheets для импорта в проект (.props)
│   ├── DefaultPaths.props    #   VC++ Directories (x64, эталон)
│   ├── DefaultPaths-x86.props  #   VC++ Directories (x86)
│   ├── DefaultPaths-ARM64.props # VC++ Directories (ARM64)
│   ├── DebugSettings.props   #   Настройки отладчика
│   ├── AdvancedSettings.props #   Advanced / C++/CLI свойства
│   ├── DLL.props             #   Настройки для Dynamic Library
│   ├── StaticLib.props       #   Настройки для Static Library
│   └── Driver.props          #   Настройки для Kernel Driver
├── scripts/                  # PowerShell-скрипты
│   ├── verify-environment.ps1  #   Диагностика окружения (SDK, VS, toolchain)
│   ├── apply-default-paths.ps1 #   Автоматическое применение эталонных путей к .vcxproj
│   └── diff-project-settings.ps1 # Сравнение проекта с эталоном
├── vs2017/                   # Конфигурации для VS 2017 (v141)
├── vs2022/                   # Конфигурации для VS 2022 (v143)
├── vs2025/                   # Конфигурации для VS 2025 (v144)
├── errors/                   # Описание частых ошибок линковки
│   ├── lnk2019-unresolved-external.md
│   ├── lnk2001-unresolved-external.md
│   ├── lnk1104-cannot-open-file.md
│   └── lnk1120-link-failed.md
├── .vsconfig                 # Файл для установки компонентов VS
├── README.md                 # Этот файл
├── general.md                # General Properties (эталон)
├── advanced.md               # Advanced Properties (эталон)
├── debugging.md              # Debugger Settings (эталон)
└── vc++-directories.md       # VC++ Directories (эталон)
```

## Quick Start

### 1. Диагностика окружения

```powershell
.\scripts\verify-environment.ps1
```

### 2. Сравнение проекта с эталоном

```powershell
.\scripts\diff-project-settings.ps1 -ProjectPath "C:\MyProject\MyProject.vcxproj"
```

### 3. Автоматическое восстановление путей

```powershell
.\scripts\apply-default-paths.ps1 -Path "C:\MyProject" -Architecture x64
```

### 4. Импорт через Property Sheets (рекомендуемый способ)

1. Откройте проект в Visual Studio.
2. View → Other Windows → Property Manager.
3. Правый клик на конфигурации → **Add Existing Property Sheet**.
4. Выберите нужный `.props` файл из папки `props/`.
5. Для x64 проектов: `props/DefaultPaths.props`.
6. Для x86 проектов: `props/DefaultPaths-x86.props`.
7. Для ARM64 проектов: `props/DefaultPaths-ARM64.props`.

## Addressing Kernel32.lib and Related Linker Issues

A known failure pattern in Visual Studio builds involves unresolved external symbols originating from the Windows SDK, most commonly manifesting as errors referencing `kernel32.lib`. These errors typically indicate that the linker is unable to locate core system libraries due to altered or missing default search paths.

In such situations, the most reliable resolution is to reset all Visual Studio directory settings to their factory defaults. This repository provides the exact reference paths and configuration structures against which a working baseline is defined. By comparing or replacing the current project and solution settings with those archived here, the standard search order for `kernel32.lib` and other foundational libraries can be fully restored.

## Recommended Workflow

1. Verify that the Windows SDK and Visual Studio build tools are installed and properly registered.
2. Open the affected project or solution and navigate to its property pages.
3. Review the `VC++ Directories` and `Linker > General` sections.
4. Cross-reference the configured paths with the defaults documented in this repository.
5. Replace any deviant entries with the default paths as shown in the archived configuration files.
6. Rebuild the project to confirm resolution of the `kernel32.lib` or related linker errors.

## Using .vsconfig

Файл `.vsconfig` можно открыть через **Visual Studio Installer** для автоматической установки необходимых компонентов:

- Откройте Visual Studio Installer.
- Нажмите **Modify** на нужной установке VS.
- Перейдите на вкладку **Import**.
- Выберите `.vsconfig` из этого репозитория.
- Установите отмеченные компоненты.

## Common Linker Errors

| Ошибка | Описание | Решение |
|---|---|---|
| LNK1104 | Cannot open file (kernel32.lib) | Восстановить пути, переустановить SDK |
| LNK2019 | Unresolved external symbol | Проверить Library Directories и зависимости |
| LNK2001 | Unresolved external symbol (subsystem) | Проверить /SUBSYSTEM и entry point |
| LNK1120 | Link failed (summary) | Смотреть первопричину в LNK2019/2001/1104 |

Подробнее: файлы в папке `errors/`.

## Scope of Support

This repository does not provide binary libraries or installers. It offers only declarative, human-readable configuration templates intended for developers familiar with Visual Studio project management. These files are provided as reference material and should be adapted to the specific version of Visual Studio and Windows SDK in use.

For persistent issues beyond path configuration, consult the official Visual Studio or Windows SDK documentation.
