<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="100">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Ameni_VS_Kernel-Configuration_Archive-5C2D91?logo=visualstudio&labelColor=222" alt="Ameni VS Kernel">
  <img src="https://img.shields.io/badge/platform-windows+linux-blue?labelColor=222" alt="Win+Linux">
  <img src="https://img.shields.io/badge/arch_linux-AUR_support-1793D1?logo=archlinux&labelColor=222" alt="Arch Linux">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?labelColor=222" alt="MIT">
</p>

<h1 align="center">Ameni VS Kernel</h1>

<p align="center">
  Агент диагностики и восстановления настроек Visual Studio.<br>
  Пошаговое руководство по исправлению ошибок линковки (LNK2019, LNK1104, LNK1120)<br>
  и приведению VC++ Directories к эталонной конфигурации.
</p>

<p align="center">
  <a href="#быстрый-старт">Быстрый старт</a> &middot;
  <a href="#установка">Установка</a> &middot;
  <a href="#cli-агент">CLI агент</a> &middot;
  <a href="#диагностика">Диагностика</a> &middot;
  <a href="#property-sheets-props">Property Sheets</a> &middot;
  <a href="#скрипты">Скрипты</a> &middot;
  <a href="#справочник-ошибок-линковки">Ошибки</a> &middot;
  <a href="#arch-linux">Arch Linux</a>
</p>

<br>

## Быстрый старт

Если сборка падает с ошибками `LNK1120`, `LNK2019` или `LNK1104`, следуйте этим шагам по порядку — от самых простых и безопасных к более сложным.

| Шаг | Действие | Описание |
|-----|----------|----------|
| 1 | **Диагностика окружения** | Проверить установку VS, Windows SDK, MSVC toolchain и наличие `kernel32.lib` |
| 2 | **Сравнение с эталоном** | Сверить текущие настройки .vcxproj с эталонными из репозитория |
| 3 | **Применить эталон через .props** | Импортировать property sheet для исправления VC++ Directories без редактирования .vcxproj |
| 4 | **Применить эталон через скрипт** | Автоматически исправить все .vcxproj в папке |
| 5 | **Ручное редактирование** | Открыть свойства проекта и исправить пути вручную |
| 6 | **Переустановка SDK/VS** | Переустановить или восстановить Windows SDK или инструменты сборки VS |

<br>

---

## Установка

### Windows (Visual Studio)

```powershell
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
.\scripts\verify-environment.ps1
```

### Arch Linux (and derivatives)

**Через AUR (PKGBUILD из репозитория):**

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
makepkg -si
```

**Или напрямую:**

```bash
sudo pacman -S powershell       # опционально, для PowerShell-скриптов
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
export PATH="$PATH:$(pwd)/.ameni/bin"
ameni vs about
```

**Зависимости Arch Linux:**

```bash
sudo pacman -S dotnet-sdk       # .NET SDK (опционально)
sudo pacman -S mono             # Mono для .NET Framework (опционально)
sudo pacman -S powershell       # PowerShell Core для запуска PS1-скриптов
```

### CLI агент

**Через symlink (рекомендуется):**

```bash
sudo ln -s "$(pwd)/.ameni/bin/ameni" /usr/local/bin/ameni
ameni vs diagnose
```

**Или через PATH:**

```bash
export PATH="$PATH:$(pwd)/.ameni/bin"
echo 'export PATH="$PATH:'"$(pwd)"'/.ameni/bin"' >> ~/.bashrc
```

<br>

---

## CLI агент

`ameni vs` предоставляет команды диагностики и проверки через единый интерфейс.

### ameni vs diagnose

**Кроссплатформенная диагностика.** Определяет ОС и запускает соответствующие проверки.

**Arch Linux:**
```
$ ameni vs diagnose

=== Environment Diagnostics ===
OS: Linux (x86_64)
[INFO]  dotnet: 9.0.201
[INFO]  mono: Mono JIT compiler version 6.12.0
[INFO]  pwsh: PowerShell 7.4.0
[INFO]  node: v22.0.0

=== Build Tools ===
[INFO]  gcc: gcc (GCC) 14.2.0
[INFO]  g++: g++ (GCC) 14.2.0
[INFO]  make: GNU Make 4.4.1
[INFO]  cmake: cmake version 3.30.0
[INFO]  clang: clang version 18.0.0
```

**Windows (Git Bash / WSL):**
```
$ ameni vs diagnose

=== Environment Diagnostics ===
OS: MINGW64_NT-10.0 (x86_64)

# PowerShell Core required for full VS diagnostics:
$ pwsh ./scripts/verify-environment.ps1
[OK] vswhere.exe found: Visual Studio Community 2022 [17.x]
[OK] Windows Kits 10: kernel32.lib found
[OK] MSVC 14.35 (VS 2022): vcruntime.lib found
```

**Windows (PowerShell):**
```powershell
PS> .ameni/bin/ameni.ps1 diagnose
```

### ameni vs check

**Инспекция .vcxproj файлов.** Проверяет корректность путей LibraryDirectories.

```
$ ameni vs check ./MyProject

=== Project Structure Check ===
Path: /home/user/MyProject
[INFO]  Found .vcxproj files:
    MyProject.vcxproj
[INFO]  Check complete.
```

**PowerShell:**
```powershell
PS> .ameni/bin/ameni.ps1 check ./MyProject
```

### ameni vs props

**Список Property Sheets.** Показывает доступные .props файлы с описанием.

```
$ ameni vs props

=== Available Property Sheets ===
  DefaultPaths          no description
  DefaultPaths-x86      no description
  DefaultPaths-ARM64    no description
  AdvancedSettings      no description
  DLL                   no description
  StaticLib             no description
  DebugSettings         no description
  Driver                no description

[INFO]  Usage: Add props via Visual Studio Property Manager
```

### ameni vs errors

**Справочник ошибок линковки.**

```
$ ameni vs errors

=== Linker Error Reference ===
  lnk1104-cannot-open-file              fatal error LNK1104: cannot open file 'kernel32.lib'
  lnk2019-unresolved-external           error LNK2019: unresolved external symbol
  lnk2001-unresolved-external           LNK2001: unresolved external symbol _main
  lnk1120-link-failed                   fatal error LNK1120: 1 unresolved externals

Usage: ameni vs errors <error-name>
Example: ameni vs errors lnk1104-cannot-open-file
```

### ameni vs help

```
ameni vs diagnose             полная диагностика (Linux/Windows)
ameni vs check [path]         проверка .vcxproj
ameni vs props                список property sheets
ameni vs errors [name]        справочник ошибок
ameni vs about                информация об агенте
ameni vs help                 справка
```

**PowerShell (Windows):** все команды доступны через `ameni.ps1`
```powershell
.ameni/bin/ameni.ps1 diagnose
.ameni/bin/ameni.ps1 check C:\MyProject
.ameni/bin/ameni.ps1 props
.ameni/bin/ameni.ps1 errors lnk1104-cannot-open-file
```

<br>

---

## Диагностика

### Шаг 1 — Проверка окружения (Windows)

Запустите скрипт проверки, чтобы убедиться, что инструменты сборки установлены и `kernel32.lib` доступен.

**PowerShell:**
```powershell
.\scripts\verify-environment.ps1
```

**Что проверяет:**
- Наличие `vswhere.exe` и установки VS
- Папку Windows SDK (`Windows Kits\10`) и файл `kernel32.lib`
- Директории MSVC toolchain и файл `vcruntime.lib`
- Ключевые переменные окружения (`VC_IncludePath`, `VC_LibraryPath_x64` и т.д.)

**Пример вывода:**
```
=== Visual Studio Environment Verification ===
[OK] vswhere.exe найден
     Установка: Visual Studio Community 2022 [17.x]
[OK] Windows Kits найден
     SDK 10.0.19041.0: kernel32.lib найден
[OK] MSVC 14.35 (VS 2022 Community)
     vcruntime.lib найден
```

Если скрипт сообщает о недостающих компонентах — переходите к шагу 6 (переустановка) или используйте `.vsconfig`.

### Шаг 2 — Сравнение с эталоном

Запустите скрипт сравнения, чтобы увидеть, какие свойства VC++ Directories отличаются от эталонных.

**PowerShell:**
```powershell
.\scripts\diff-project-settings.ps1 -ProjectPath "C:\MyProject\MyProject.vcxproj"
```

**Формат вывода:**
```
=== Diff: проект vs эталон ===
Файл: C:\MyProject\MyProject.vcxproj

  [OK] ExecutableDirectories
  [!] LibraryDirectories
      Сейчас:   $(VC_LibraryPath_x64);C:\Custom\Lib
      Эталон:  $(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64
  [OK] IncludeDirectories
```

Если все пункты показывают `[OK]` — ваши VC++ Directories совпадают с эталоном. Переходите к справочнику ошибок.

### Шаг 3 — Применение эталона через .props (рекомендуется)

Безопасный метод исправления путей без изменения `.vcxproj`.

1. Откройте **Property Manager** в VS (View -> Property Manager)
2. Кликните правой кнопкой на конфигурации проекта
3. Выберите **Add Existing Property Sheet...**
4. Укажите `props/DefaultPaths.props`
5. При необходимости добавьте `props/AdvancedSettings.props`

### Шаг 4 — Применение эталона через скрипт

Автоматически исправляет все `.vcxproj` в указанной папке.

**PowerShell:**
```powershell
.\scripts\apply-default-paths.ps1 -Path "C:\Projects\MyApp" -Architecture x64
```

### Шаг 5 — Ручное редактирование

Откройте свойства проекта и исправьте пути вручную согласно эталонным значениям.

### Шаг 6 — Переустановка SDK/VS

Используйте `.vsconfig` из корня репозитория:

1. Откройте **Visual Studio Installer**
2. Нажмите **Изменить** у вашего экземпляра VS
3. Выберите вкладку **Импорт**
4. Найдите и выберите `.vsconfig`
5. Нажмите **Установить**

<br>

---

## Property Sheets (.props)

Папка `props/` содержит эталонные Property Sheets.

| Файл | Назначение |
|------|------------|
| `DefaultPaths.props` | Базовые пути для x64 (VC++ Directories) |
| `DefaultPaths-x86.props` | Базовые пути для x86 |
| `DefaultPaths-ARM64.props` | Базовые пути для ARM64 |
| `AdvancedSettings.props` | Дополнительные настройки C/C++ |
| `DLL.props` | Настройки для сборки DLL |
| `StaticLib.props` | Настройки для сборки статической библиотеки |
| `DebugSettings.props` | Отладочные настройки |
| `Driver.props` | Настройки для драйверов |

<br>

---

## Скрипты

Папка `scripts/` содержит PowerShell-скрипты.

| Скрипт | Назначение | Параметры |
|--------|------------|-----------|
| `verify-environment.ps1` | Проверяет установку VS, Windows SDK, MSVC и наличие `kernel32.lib` | Нет |
| `diff-project-settings.ps1` | Сравнивает `.vcxproj` с эталонными VC++ Directories | `-ProjectPath <string>` (обязательно) |
| `apply-default-paths.ps1` | Применяет эталонные пути ко всем `.vcxproj` в папке | `-Path <string>` (по умолч. `.`), `-Architecture <x64\|x86\|ARM64>`, `-Backup <bool>` |

На **Arch Linux** скрипты выполняются через PowerShell Core:

```bash
sudo pacman -S powershell
pwsh ./scripts/verify-environment.ps1
```

<br>

---

## Справочник ошибок линковки

Папка `errors/` содержит объяснения распространённых ошибок.

| Файл | Ошибка | Быстрое решение |
|------|--------|-----------------|
| `errors/lnk1104-cannot-open-file.md` | LNK1104 | Восстановить Library Directories или переустановить Windows SDK |
| `errors/lnk2019-unresolved-external.md` | LNK2019 | Проверить Library Directories и Additional Dependencies |
| `errors/lnk2001-unresolved-external.md` | LNK2001 | Проверить /SUBSYSTEM (console vs windows) |
| `errors/lnk1120-link-failed.md` | LNK1120 | Посмотреть на первопричину в LNK2019/2001/1104 |

<br>

---

## Конфиги по версиям VS

| Папка | Версия VS | Platform Toolset |
|-------|-----------|------------------|
| `vs2017/` | Visual Studio 2017 | v141 |
| `vs2022/` | Visual Studio 2022 | v143 |
| `vs2025/` | Visual Studio 2025 | v144 |

В каждой папке — `general.md` и `vc++-directories.md` под соответствующий toolset.

<br>

---

## Кроссплатформенное использование

### Arch Linux

**Зависимости:**

```bash
sudo pacman -S dotnet-sdk       # .NET SDK (рекомендуется)
sudo pacman -S powershell       # PowerShell Core (для запуска PS1)
sudo pacman -S mono             # Mono (опционально)
```

**Установка из PKGBUILD:**

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
makepkg -si
ameni vs diagnose
```

**Или вручную:**

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
export PATH="$PATH:$(pwd)/.ameni/bin"
ameni vs diagnose
```

**Полезные пакеты:**

```bash
sudo pacman -S base-devel cmake gcc clang lldb boost
sudo pacman -S dotnet-sdk dotnet-runtime
```

### Windows

**Требования:** Git Bash, WSL или PowerShell Core (pwsh).

**Git Bash / WSL:**

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
export PATH="$PATH:$(pwd)/.ameni/bin"
ameni vs diagnose
```

**PowerShell (без bash):**

```powershell
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
.ameni/bin/ameni.ps1 diagnose
.ameni/bin/ameni.ps1 check C:\MyProject
.ameni/bin/ameni.ps1 props
.ameni/bin/ameni.ps1 errors lnk1104-cannot-open-file
```

### Соответствие команд

| Команда | Arch Linux (bash) | Windows (PowerShell) |
|---------|-------------------|---------------------|
| `diagnose` | `ameni vs diagnose` | `.ameni/bin/ameni.ps1 diagnose` |
| `check` | `ameni vs check ./path` | `.ameni/bin/ameni.ps1 check ./path` |
| `props` | `ameni vs props` | `.ameni/bin/ameni.ps1 props` |
| `errors` | `ameni vs errors lnk1104` | `.ameni/bin/ameni.ps1 errors lnk1104` |
| `help` | `ameni vs help` | `.ameni/bin/ameni.ps1 help` |

Все команды идентичны по функционалу на обеих платформах.

---

<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="32">
  <br>
  <a href="https://github.com/inzexg-coder">@inzexg-coder</a>
</p>
