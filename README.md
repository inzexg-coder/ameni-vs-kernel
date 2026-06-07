<p align="center">
  <img src="https://img.shields.io/badge/Visual%20Studio-Configuration%20Archive-blue?logo=visualstudio">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey">
</p>

<br>

<h1 align="center">Visual Studio Configuration Archive</h1>

<p align="center">
  <b>EN</b> · Эталонные конфигурации Visual Studio для восстановления проектных настроек,<br>
  устранения ошибок линковки и диагностики сборочного окружения.
</p>

<p align="center">
  <b>RU</b> · Reference Visual Studio configurations for restoring project settings,<br>
  fixing linker errors, and diagnosing the build environment.
</p>

---

<p align="center">
  <!-- EN Quick Start --> <b>EN:</b> Jump to <a href="#quick-start">Quick Start</a> ·
  <a href="#reference-configuration">Reference Configuration</a> ·
  <a href="#scripts">Scripts</a> ·
  <a href="#version-specific-configs">Versions</a>
</p>
<p align="center">
  <!-- RU Быстрый старт --> <b>RU:</b> Перейти к <a href="#Быстрый-старт">Быстрому старту</a> ·
  <a href="#Эталонная-конфигурация">Эталонной конфигурации</a> ·
  <a href="#Скрипты">Скриптам</a> ·
  <a href="#Конфиги-по-версиям">Версиям</a>
</p>

---

## English

### Overview

This repository stores **reference Visual Studio project configurations** — a recoverable
baseline of include directories, library directories, and linker dependencies as they appear
in a standard VS installation. Its purpose is to help you quickly restore default settings
when build configurations get corrupted or misaligned, most commonly fixing `kernel32.lib`
and related linker errors.

### Quick Start

#### Scenario: Build fails with LNK1120 / LNK2019

**Step 1 — diagnose the environment:**
```powershell
.\scripts\verify-environment.ps1
```
If it reports missing components — install them via `.vsconfig`.

**Step 2 — compare with reference:**
```powershell
.\scripts\diff-project-settings.ps1 -ProjectPath "YourProject.vcxproj"
```
See which paths differ from the reference.

**Step 3 — apply reference paths:**
```powershell
# Automatic restore:
.\scripts\apply-default-paths.ps1 -Path "C:\SolutionDir" -Architecture x64

# Or via Property Manager (recommended):
#   Add props/DefaultPaths.props to your project
```

**Step 4 — rebuild:**
```powershell
# Clean + Rebuild in Visual Studio, or via MSBuild:
msbuild YourProject.vcxproj /t:Rebuild /p:Configuration=Release
```

#### Scenario: Fresh VS installation

1. Import `.vsconfig` into Visual Studio Installer.
2. Install the components.
3. Attach `DefaultPaths.props` via Property Manager.

---

### Reference Configuration

Baseline configuration files in the repository root describe the exact reference values
for every important project property. These are the settings that a clean VS installation
would use by default.

| File | Description |
|---|---|
| `vc++-directories.md` | VC++ Directories — the most critical section for `kernel32.lib` resolution |
| `general.md` | General Properties — output dirs, platform toolset, SDK version |
| `advanced.md` | Advanced + C++/CLI Properties — debug libs, character set, WPO |
| `debugging.md` | Debugger Settings — working dir, debugger type, environment |

### Property Sheets (.props)

These are MSBuild XML files you can import via **Property Manager**
(`View → Other Windows → Property Manager` → right-click → Add Existing Property Sheet).
They apply reference settings to any `.vcxproj` without modifying the project file itself.

| File | Platform | Purpose |
|---|---|---|
| `props/DefaultPaths.props` | x64 | Reference VC++ Directories (most common) |
| `props/DefaultPaths-x86.props` | x86 | Reference VC++ Directories for 32-bit |
| `props/DefaultPaths-ARM64.props` | ARM64 | Reference VC++ Directories for ARM64 |
| `props/DebugSettings.props` | any | Debugger configuration reference |
| `props/AdvancedSettings.props` | any | Advanced + C++/CLI settings reference |
| `props/DLL.props` | x64 | Minimal setup for Dynamic Library (.dll) |
| `props/StaticLib.props` | x64 | Minimal setup for Static Library (.lib) |
| `props/Driver.props` | x64 | Minimal setup for Kernel Driver (.sys) |

### Scripts

| Script | What it does |
|---|---|
| `scripts/verify-environment.ps1` | Checks if VS, Windows SDK, MSVC are installed and `kernel32.lib` exists |
| `scripts/diff-project-settings.ps1` | Compares a `.vcxproj` against reference paths |
| `scripts/apply-default-paths.ps1` | Automatically restores reference paths in all `.vcxproj` files |

### Version-Specific Configs

Visual Studio versions differ in Platform Toolset and default paths.

| Folder | Toolset | Notes |
|---|---|---|
| `vs2017/` | v141 | MSVC 14.1x, `Windows Kits\10` |
| `vs2022/` | v143 | MSVC 14.3x, matches root reference exactly |
| `vs2025/` | v144 | MSVC 14.4x, may use Windows SDK 11.0 |

### Linker Error Reference

| Folder / File | Error | Quick fix |
|---|---|---|
| `errors/lnk1104-cannot-open-file.md` | LNK1104 | Restore Library Directories or reinstall SDK |
| `errors/lnk2019-unresolved-external.md` | LNK2019 | Check Library Directories & Additional Dependencies |
| `errors/lnk2001-unresolved-external.md` | LNK2001 | Check /SUBSYSTEM matches entry point |
| `errors/lnk1120-link-failed.md` | LNK1120 | Look at the underlying LNK2019/2001/1104 error |

### .vsconfig — VS Component Manifest

Import `.vsconfig` into **Visual Studio Installer** (`Modify → Import`) to automatically
select the required components: MSVC toolsets (v141, v143), Windows 10/11 SDKs,
CMake support, ATL, MFC, Clang, and MSBuild.

### Support

This repository provides only configuration files and documentation — no binaries
or installers. For issues beyond path configuration, refer to:

- [Visual Studio documentation](https://docs.microsoft.com/en-us/visualstudio/)
- [Windows SDK documentation](https://docs.microsoft.com/en-us/windows/win32/)
- [Microsoft Q&A — Visual Studio](https://docs.microsoft.com/en-us/answers/topics/visual-studio.html)

---

<br>

---

## Русский

### Описание

Репозиторий содержит **эталонные конфигурации Visual Studio** — проверенные настройки
путей к заголовочным файлам, библиотекам и линковщику, которые можно использовать
для быстрого восстановления сборки после повреждения конфигурации проекта.
Наиболее частый сценарий — исправление ошибок, связанных с `kernel32.lib`.

### Быстрый старт

#### Ситуация: сборка падает с LNK1120 / LNK2019

**Шаг 1 — диагностика окружения:**
```powershell
.\scripts\verify-environment.ps1
```
Если не хватает компонентов — установить через `.vsconfig`.

**Шаг 2 — сравнить с эталоном:**
```powershell
.\scripts\diff-project-settings.ps1 -ProjectPath "ВашПроект.vcxproj"
```
Посмотреть, какие пути отличаются от эталонных.

**Шаг 3 — применить эталонные пути:**
```powershell
# Автоматически:
.\scripts\apply-default-paths.ps1 -Path "C:\SolutionDir" -Architecture x64

# Или через Property Manager (рекомендуется):
#   Добавить props/DefaultPaths.props к проекту
```

**Шаг 4 — пересобрать:**
```powershell
# Clean + Rebuild в студии, или через MSBuild:
msbuild ВашПроект.vcxproj /t:Rebuild /p:Configuration=Release
```

#### Ситуация: новая установка VS

1. Импортировать `.vsconfig` в Visual Studio Installer.
2. Установить компоненты.
3. Подключить `DefaultPaths.props` через Property Manager.

---

### Эталонная конфигурация

Файлы в корне репозитория описывают точные эталонные значения
для каждой важной группы свойств — те настройки, которые VS выставляет
по умолчанию при чистой установке.

| Файл | Описание |
|---|---|
| `vc++-directories.md` | **VC++ Directories** — критический раздел для `kernel32.lib` |
| `general.md` | General Properties — выходные папки, toolset, версия SDK |
| `advanced.md` | Advanced + C++/CLI — debug-библиотеки, кодировка, WPO |
| `debugging.md` | Debugger Settings — рабочая папка, тип отладчика, окружение |

### Property Sheets (.props)

MSBuild XML-файлы для импорта через **Property Manager**
(`View → Other Windows → Property Manager` → правый клик → Add Existing Property Sheet).
Применяют эталонные настройки без изменения `.vcxproj`.

| Файл | Платформа | Назначение |
|---|---|---|
| `props/DefaultPaths.props` | x64 | Эталонные VC++ Directories (основной) |
| `props/DefaultPaths-x86.props` | x86 | Эталонные пути для 32-битных проектов |
| `props/DefaultPaths-ARM64.props` | ARM64 | Эталонные пути для ARM64 |
| `props/DebugSettings.props` | любая | Эталонные настройки отладчика |
| `props/AdvancedSettings.props` | любая | Advanced + C++/CLI свойства |
| `props/DLL.props` | x64 | Динамическая библиотека (.dll) |
| `props/StaticLib.props` | x64 | Статическая библиотека (.lib) |
| `props/Driver.props` | x64 | Драйвер ядра (.sys) |

### Скрипты

| Скрипт | Что делает |
|---|---|
| `scripts/verify-environment.ps1` | Проверяет установку VS, Windows SDK, MSVC, наличие `kernel32.lib` |
| `scripts/diff-project-settings.ps1` | Сравнивает `.vcxproj` с эталонными путями |
| `scripts/apply-default-paths.ps1` | Автоматически восстанавливает эталонные пути в `.vcxproj` |

### Конфиги по версиям

| Папка | Toolset | Особенности |
|---|---|---|
| `vs2017/` | v141 | MSVC 14.1x, `Windows Kits\10` |
| `vs2022/` | v143 | MSVC 14.3x, полностью совпадает с корневым эталоном |
| `vs2025/` | v144 | MSVC 14.4x, может использовать Windows SDK 11.0 |

### Справочник ошибок линковки

| Файл | Ошибка | Быстрое решение |
|---|---|---|
| `errors/lnk1104-cannot-open-file.md` | LNK1104 | Восстановить Library Directories или SDK |
| `errors/lnk2019-unresolved-external.md` | LNK2019 | Проверить Library Directories и зависимости |
| `errors/lnk2001-unresolved-external.md` | LNK2001 | Проверить /SUBSYSTEM и точку входа |
| `errors/lnk1120-link-failed.md` | LNK1120 | Смотреть первопричину в LNK2019/2001/1104 |

### .vsconfig — манифест компонентов VS

Импортируйте `.vsconfig` в **Visual Studio Installer** (`Modify → Import`), чтобы
автоматически отметить необходимые компоненты: MSVC (v141, v143), Windows 10/11 SDK,
CMake, ATL, MFC, Clang и MSBuild.

### Поддержка

Репозиторий предоставляет только конфигурационные файлы и документацию —
без бинарников и установщиков. Для проблем, выходящих за рамки путей:

- [Документация Visual Studio](https://docs.microsoft.com/en-us/visualstudio/)
- [Документация Windows SDK](https://docs.microsoft.com/en-us/windows/win32/)
- [Microsoft Q&A — Visual Studio](https://docs.microsoft.com/en-us/answers/topics/visual-studio.html)
