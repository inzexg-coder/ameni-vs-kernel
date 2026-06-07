<p align="center">
  <img src="https://img.shields.io/badge/Visual%20Studio-Configuration%20Archive-blue?logo=visualstudio">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey">
</p>

<br>

<h1 align="center">Visual Studio Configuration Archive</h1>

<p align="center">
  <b>EN</b> · Step‑by‑step guide to fix linker errors (kernel32.lib, LNK2019, LNK1104) and restore VS project settings<br>
  <b>RU</b> · Пошаговое руководство по исправлению ошибок линковки (kernel32.lib, LNK2019, LNK1104) и восстановлению настроек проектов VS
</p>

---

## 📖 Table of Contents / Содержание
- [Quick Start / Быстрый старт](#quick-start--быстрый-старт)
- [Step‑by‑Step Troubleshooting / Пошаговое устранение неполадок](#step-by-step-troubleshooting--пошаговое-устранение-неполадок)
- [Reference Configuration / Эталонная конфигурация](#reference-configuration--эталонная-конфигурация)
- [Property Sheets (.props) / Property Sheets (.props)](#propertysheets-props--propertysheets-props)
- [PowerShell Scripts / PowerShell‑скрипты](#powershell-scripts--powershell-скрипты)
- [Version‑Specific Configs / Конфиги по версиям VS](#version-specific-configs--конфиги-по-версиям-vs)
- [Linker Error Reference / Справочник ошибок линковки](#linker-error-reference--справочник-ошибок-линковки)
- [.vsconfig — VS Component Manifest / .vsconfig — манифест компонентов VS](#vsconfig---vs-component-manifest-vsconfig---манифест-компонентов-vs)

---

## 🚀 Quick Start / Быстрый старт

If your build fails with errors like `LNK1120`, `LNK2019` or `LNK1104`, follow these steps **in order** — from simplest/safest to more advanced/risky.

Если сборка падает с ошибками `LNK1120`, `LNK2019` или `LNK1104`, выполняйте шаги **по порядку** — от самых простых и безопасных к более сложным/рискованным.

| Step / Шаг | Action / Действие | EN Description | RU Description |
|---|---|---|---|
| 1 | 🔍 **Diagnose environment** | Verify VS, Windows SDK, MSVC toolchain and presence of `kernel32.lib` | Проверить установку VS, Windows SDK, MSVC toolchain и наличие `kernel32.lib` |
| 2 | 📊 **Compare with reference** | Check current .vcxproj settings against the archived baseline | Сверить текущие настройки .vcxproj с эталонными из репозитория |
| 3 | 🛠️ **Apply reference via .props** (recommended) | Import a property sheet to fix VC++ Directories without editing .vcxproj | Импортировать property sheet для исправления VC++ Directories без изменения .vcxproj |
| 4 | ⚙️ **Apply reference via script** | Automatically patch all .vcxproj files in a folder | Автоматически исправить все .vcxproj в папке |
| 5 | 🔧 **Manual edit** | Open project properties and correct paths manually | Открыть свойства проекта и исправить пути вручную |
| 6 | 💾 **Reinstall SDK/VS** | Repair or reinstall Windows SDK or Visual Studio build tools | Переустановить или восстановить Windows SDK или инструменты сборки VS |

---

## 🛠️ Step‑by‑Step Troubleshooting / Пошаговое устранение неполадок

### Step 1 — Diagnose environment / Шаг 1 — Диагностика окружения

Run the verification script to ensure the build tools are installed and `kernel32.lib` exists.

Запустите скрипт проверки, чтобы убедиться, что инструменты сборки установлены и `kernel32.lib` доступен.

**PowerShell:**
```powershell
# From repository root:
.\scripts\verify-environment.ps1
```

**What it checks / Что проверяет:**
- Presence of `vswhere.exe` → VS installations
- Windows SDK folder (`Windows Kits\10`) and `kernel32.lib`
- MSVC toolchain directories and `vcruntime.lib`
- Key environment variables (`VC_IncludePath`, `VC_LibraryPath_x64`, etc.)

**Sample output / Пример вывода:**
```
=== Visual Studio Environment Verification ===
[OK] vswhere.exe найден
     Установка: Visual Studio Community 2022 [17.x]
[OK] Windows Kits найден
     SDK 10.0.19041.0: kernel32.lib найден
[OK] MSVC 14.35 (VS 2022 Community)
     vcruntime.lib найден
```

If the script reports missing components → proceed to **Step 6** (reinstall) or use `.vsconfig` to install them.

Если скрипт сообщает об отсутствующих компонентах → переходите к **Шагу 6** (переустановка) или используйте `.vsconfig` для их установки.

---

### Step 2 — Compare with reference / Шаг 2 — Сравнение с эталоном

Use the diff script to see which VC++ Directory properties deviate from the reference.

Запустите скрипт сравнения, чтобы увидеть, какие свойства VC++ Directories отличаются от эталонных.

**PowerShell:**
```powershell
# Specify full path to your .vcxproj
.\scripts\diff-project-settings.ps1 -ProjectPath "C:\MyProject\MyProject.vcxproj"
```

**Output format / Формат вывода:**
```
=== Diff: проект vs эталон ===
Файл: C:\MyProject\MyProject.vcxproj

  [OK] ExecutableDirectories
  [!] LibraryDirectories
      Сейчас:   $(VC_LibraryPath_x64);C:\Custom\Lib
      Эталон:  $(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64
  [OK] IncludeDirectories
```

If all items show `[OK]` → your VC++ Directories already match the reference; the issue may be elsewhere (see linker errors below).

Если все пункты показывают `[OK]` → ваши VC++ Directories уже совпадают с эталоном; проблема может быть в другом (см. справочник ошибок ниже).

---

### Step 3 — Apply reference via .props (recommended) / Шаг 3 — Применение эталонного через .props (рекомендуется)

Property Sheets let you apply reference settings without touching the .vcxproj file. This is the safest and most reversible method.

Property Sheets позволяют применять эталонные настройки без изменения .vcxproj файла. Это самый безопасный и обратимый способ.

**How to do it / Как сделать:**
1. In Visual Studio, open **View → Other Windows → Property Manager**
2. Right‑click the configuration (e.g. `Debug|x64`) → **Add Existing Property Sheet…**
3. Browse to the repository and select:
   - `props/DefaultPaths.props` for x64 projects
   - `props/DefaultPaths-x86.props` for x86 projects
   - `props/DefaultPaths-ARM64.props` for ARM64 projects
4. Click **OK**, then **Rebuild** the solution.

**To undo / Отмена:**
Simply remove the property sheet from Property Manager — no changes remain in the .vcxproj.

Просто удалите property sheet из Property Manager — изменений в .vcxproj не останется.

---

### Step 4 — Apply reference via script / Шаг 4 — Применение эталонного через скрипт

Use this when you need to fix many projects at once or prefer a fully automated approach. The script creates `.bak` files before changing anything.

Используйте этот метод, когда нужно поправить множество проектов сразу или предпочитаете полностью автоматизированный подход. Скрипт создаёт `.bak` копии перед изменением.

**PowerShell:**
```powershell
# Fix all .vcxproj under a folder (default: current directory)
.\scripts\apply-default-paths.ps1

# Specify folder and architecture explicitly
.\scripts\apply-default-paths.ps1 -Path "C:\SolutionRoot" -Architecture x64

# Skip backups (not recommended)
.\scripts\apply-default-paths.ps1 -Backup $false
```

**What it does / Что делает:**
- Recursively finds all `*.vcxproj` files
- For each file:
  1. Creates `<file>.vcxproj.bak` (if `-Backup $true`)
  2. Replaces `LibraryDirectories`, `IncludeDirectories`, `ExecutableDirectories` with the reference values for the chosen architecture
  3. Saves the file

**To restore / Откат:**
Rename each `.bak` file back to `.vcxproj` or delete the modified files and restore from version control.

Переименуйте каждый `.bak` файл обратно в `.vcxproj` или удалите изменённые файлы и восстановите их из системы контроля версий.

---

### Step 5 — Manual edit / Шаг 5 — Ручное редактирование

Only use this if the previous steps fail or you need to adjust a single setting.

Применяйте только если предыдущие шаги не помогли или нужно отредактировать одну настройку.

**Where to go / Где идти:**
1. Right‑click the project → **Properties**
2. Navigate to **Configuration Properties → VC++ Directories**
3. Edit the following fields (values differ by architecture):

| Property | x64 reference value |
|---|---|
| **Library Directories** | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |
| **Include Directories** | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| **Executable Directories** | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |

4. Click **OK** → **Rebuild**.

**Tip / Совет:** Keep a copy of the original values before changing, in case you need to revert.

Совет: Сохраните копию исходных значений перед изменением, чтобы можно было откатиться.

---

### Step 6 — Reinstall SDK / Visual Studio / Шаг 6 — Переустановка SDK / Visual Studio

Use this only if diagnostics show that files are missing or corrupted.

Применяйте только если диагностика показывает отсутствие или повреждение файлов.

**Reinstall Windows SDK:**
1. Open **Visual Studio Installer**
2. Click **Modify** on your VS instance
3. Go to **Individual components**
4. Find and check:
   - `Windows 10 SDK (10.0.19041.0)` or latest
   - `Windows 11 SDK (10.0.22621.0)` (if using VS 2022+)
5. Click **Modify** to install

**Repair Visual Studio Build Tools:**
In the same installer, choose **Repair** instead of Modify.

**Alternative — use .vsconfig:**  
The file `.vsconfig` in the repository root lists the exact components needed for native C++ development. Import it via **Modify → Import** in the Visual Studio Installer to get a consistent set.

Файл `.vsconfig` в корне репозитория содержит точный список необходимых компонентов. Импортируйте его через **Modify → Import** в Visual Studio Installer, чтобы получить согласованный набор.

---

## 📚 Reference Configuration / Эталонная конфигурация

The files in the repository root describe the exact baseline values for the most important project property groups.

Файлы в корне репозитория описывают точные эталонные значения для самых важных групп свойств проекта.

| File | Description |
|---|---|
| `vc++-directories.md` | **VC++ Directories** — controls where the compiler/linker look for headers, libs, and tools. The `Library Directories` entry is the key to fixing `kernel32.lib`. |
| `general.md` | **General Properties** — output directories, intermediate directory, platform toolset, Windows SDK version, configuration type. |
| `advanced.md` | **Advanced Properties** — debug library usage, character set, whole program optimization, MFC, C++/CLI settings. |
| `debugging.md` | **Debugger Settings** — working directory, debugger type, environment variables, accelerator for C++ AMP. |

These files are meant for **reference** — compare them to your project settings or use the provided `.props` files/scripts to apply them.

Эти файлы предназначены для **справочного использования** — сравнивайте их с настройками вашего проекта или применяйте через предоставленные `.props` файлы и скрипты.

---

## 🧩 Property Sheets (.props) / Property Sheets (.props)

Property Sheets are MSBuild XML files that can be attached to any `.vcxproj` via **Property Manager**. They apply settings without modifying the project file itself.

Property Sheets — это MSBuild XML-файлы, которые можно подключать к любому `.vcxproj` через **Property Manager**. Они применяют настройки без изменения самого файла проекта.

| File | Platform | Purpose |
|---|---|---|
| `props/DefaultPaths.props` | x64 | Reference VC++ Directories (most common) |
| `props/DefaultPaths-x86.props` | x86 | Reference VC++ Directories for 32‑bit projects |
| `props/DefaultPaths-ARM64.props` | ARM64 | Reference VC++ Directories for ARM64 projects |
| `props/DebugSettings.props` | any | Debugger configuration reference |
| `props/AdvancedSettings.props` | any | Advanced + C++/CLI settings reference |
| `props/DLL.props` | x64 | Minimal setup for Dynamic Library (.dll) |
| `props/StaticLib.props` | x64 | Minimal setup for Static Library (.lib) |
| `props/Driver.props` | x64 | Minimal setup for Kernel Driver (.sys) |

### Example .props content (DefaultPaths.props)
```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2004">
  <PropertyGroup>
    <ExecutableDirectories>$(VC_ExecutablePath_x64);$(CommonExecutablePath)</ExecutableDirectories>
    <IncludeDirectories>$(VC_IncludePath);$(WindowsSDK_IncludePath);</IncludeDirectories>
    <ExternalIncludeDirectories>$(VC_IncludePath);$(WindowsSDK_IncludePath);</ExternalIncludeDirectories>
    <ReferenceDirectories>$(VC_ReferencesPath_x64);</ReferenceDirectories>
    <LibraryDirectories>$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64</LibraryDirectories>
    <LibraryWinRTDirectories>$(WindowsSDK_MetadataPath);</LibraryWinRTDirectories>
    <SourceDirectories>$(VC_SourcePath);</SourceDirectories>
    <ExcludeDirectories>$(VC_SourcePath);</ExcludeDirectories>
  </PropertyGroup>
</Project>
```

---

## ⚙️ PowerShell Scripts / PowerShell‑скрипты

The `scripts/` folder contains three utilities for diagnosing and fixing VS project configurations.

Папка `scripts/` содержит три утилиты для диагностики и исправления конфигураций проектов VS.

| Script | What it does | Parameters |
|---|---|---|
| `scripts/verify-environment.ps1` | Checks VS, Windows SDK, MSVC installation and `kernel32.lib` presence | None |
| `scripts/diff-project-settings.ps1` | Compares a `.vcxproj` against the reference VC++ Directories | `-ProjectPath <string>` (required) |
| `scripts/apply-default-paths.ps1` | Applies reference paths to all `.vcxproj` files in a folder | `-Path <string>` (default: `.`)<br>`-Architecture <x64\|x86\|ARM64>` (default: `x64`)<br>`-Backup <bool>` (default: `$true`) |

All scripts are **comment‑free** — only executable code and parameter definitions remain.

Все скрипты **без комментариев** — остался только исполняемый код и определения параметров.

---

## 🏷️ Version‑Specific Configs / Конфиги по версиям VS

Different Visual Studio versions use different Platform Toolsets and may have slight path variations.

Разные версии Visual Studio используют разные Platform Toolset и могут иметь небольшие различия в путях.

| Folder | VS Version | Platform Toolset | Notes |
|---|---|---|---|
| `vs2017/` | Visual Studio 2017 | v141 | MSVC 14.1x, Windows Kits\10 |
| `vs2022/` | Visual Studio 2022 | v143 | MSVC 14.3x — matches root reference exactly |
| `vs2025/` | Visual Studio 2025 | v144 | MSVC 14.4x — may use Windows SDK 11.0 |

Each version folder contains `general.md` and `vc++-directories.md` tailored to that toolset.

В каждой папке версии находятся файлы `general.md` и `vc++-directories.md`, адаптированные под соответствующий toolset.

---

## 🔗 Linker Error Reference / Справочник ошибок линковки

The `errors/` folder contains detailed explanations of common linker failures, their symptoms, causes, and fixes.

Папка `errors/` содержит подробные объяснения распространённых ошибок линковки, их симптомов, причин и способов решения.

| File | Error | Typical symptoms | Quick fix |
|---|---|---|---|
| `errors/lnk1104-cannot-open-file.md` | **LNK1104** | `fatal error LNK1104: cannot open file 'kernel32.lib'` | Restore Library Directories or reinstall Windows SDK |
| `errors/lnk2019-unresolved-external.md` | **LNK2019** | `error LNK2019: unresolved external symbol _WinMain@16` | Check Library Directories and Additional Dependencies |
| `errors/lnk2001-unresolved-external.md` | **LNK2001** | `LNK2001: unresolved external symbol _main` | Verify `/SUBSYSTEM` matches entry point (`console` vs `windows`) |
| `errors/lnk1120-link-failed.md` | **LNK1120** | `fatal error LNK1120: 1 unresolved externals` | Look at the underlying LNK2019/2001/1104 error |

Each file includes:
- A brief description of the error
- Common causes
- Step‑by‑step resolution instructions
- Notes on when to escalate to the next troubleshooting step

В каждом файле:
- Краткое описание ошибки
- Типичные причины
- Пошаговые инструкции по устранению
- Примечания о том, когда следует переходить к следующему шагу диагностики

---

## 🧩 .vsconfig — VS Component Manifest / .vsconfig — манифест компонентов VS

The file `.vsconfig` in the repository root tells the **Visual Studio Installer** which components to install for native C++ development.

Файл `.vsconfig` в корне репозитория указывает **Visual Studio Installer**, какие компоненты установить для разработки нативного C++.

### How to use / Как использовать
1. Open **Visual Studio Installer**
2. Click **Modify** on your VS instance
3. Select the **Import** tab
4. Browse to and select `.vsconfig` from this repository
5. Click **Install** (or **Update**) to apply the component list

### What it includes / Что включает
The manifest selects:
- **Workload**: `.NET Desktop Development` and `Desktop development with C++`
- **Individual components**:
  - MSVC v141 and v143 toolsets (x86, x64, ARM64)
  - Windows 10 SDK (10.0.19041.0) and Windows 11 SDK (10.0.22621.0)
  - CMake, ATL, MFC, Clang/LLVM for Windows
  - MSBuild and related build tools

Using `.vsconfig` ensures you have the exact toolsets and SDKs that match the reference configurations in this repository.

Использование `.vsconfig` гарантирует, что у вас установлены точно те наборы инструментов и SDK, которые соответствуют эталонным конфигурациям в этом репозитории.

---

## 📄 License / Лицензия

This repository provides only configuration files and documentation.  
No binaries, installers, or proprietary code are included.  
You are free to use, copy, and modify the files for your own projects.

Данный репозиторий предоставляет только конфигурационные файлы и документацию.  
Бинарные файлы, установщики и проприетарный код не включены.  
Вы можете свободно использовать, копировать и изменять файлы для своих проектов.

