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

**Полная диагностика окружения.** Автоматически определяет платформу и запускает соответствующие проверки.

```
$ ameni vs diagnose

=== Environment Diagnostics ===
Platform: linux (x86_64)
[INFO]  Running Linux diagnostics
[INFO]  dotnet SDK: 9.0.201 (9.0.102-preview.1...)
[INFO]  Mono: Mono JIT compiler version 6.12.0
[INFO]  PowerShell Core: PowerShell 7.4.0
[INFO]  VS Code available for C++ editing
[INFO]  gcc: /usr/bin/gcc
[INFO]  g++: /usr/bin/g++
[INFO]  make: /usr/bin/make
[INFO]  cmake: /usr/bin/cmake
[INFO]  clang: /usr/bin/clang
```

На Windows переключается на PowerShell-скрипт проверки:

```
$ ameni vs diagnose

=== Environment Diagnostics ===
Platform: windows (AMD64)
[OK] vswhere.exe found: Visual Studio Community 2022 [17.x]
[OK] Windows Kits 10: kernel32.lib found
[OK] MSVC 14.35 (VS 2022): vcruntime.lib found
```

### ameni vs check

**Инспекция .vcxproj файлов.** Проверяет корректность путей VC++ Directories.

```
$ ameni vs check ./MyProject

=== Project Structure Check ===
Path: /home/user/MyProject

[INFO]  Found .vcxproj files:
    MyProject.vcxproj
    MyProject.vcxproj.filters
[INFO]  Found 12 .props files (reference configurations available)
[INFO]  No obvious issues detected
```

### ameni vs help

```
ameni vs diagnose          — полная диагностика окружения
ameni vs check [path]      — проверка .vcxproj проекта
ameni vs about             — информация об агенте
ameni vs help              — справка
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

## Arch Linux

### Назначение репозитория на Linux

Данный репозиторий предназначен в первую очередь для диагностики Visual Studio под Windows. На Arch Linux он служит:

1. **Эталонная документация** — все описания путей, переменных и конфигураций доступны для чтения
2. **Property Sheets** — `.props` файлы можно адаптировать для кросс-компиляции
3. **Справочник ошибок** — описания LNK-ошибок актуальны независимо от платформы
4. **CLI агент** — `ameni vs` предоставляет диагностику Linux-окружения и проверку проектов

### Установка на Arch Linux

**Зависимости:**

```bash
sudo pacman -S dotnet-sdk       # .NET SDK  (рекомендуется)
sudo pacman -S powershell       # PowerShell Core (для запуска PS1-скриптов)
sudo pacman -S mono             # Mono (опционально)
```

**Установка из PKGBUILD:**

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
makepkg -si
```

**Или ручная установка:**

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
sudo ln -s "$(pwd)/.ameni/bin/ameni" /usr/local/bin/ameni
```

### Диагностика через ameni

```bash
ameni vs diagnose
```

Вывод включает: версию dotnet SDK, Mono, PowerShell Core, наличие build-инструментов (gcc, g++, make, cmake, clang).

### Полезные пакеты Arch для C++ разработки

```bash
# Основные инструменты
sudo pacman -S base-devel cmake

# Компиляторы
sudo pacman -S gcc clang lldb

# Библиотеки
sudo pacman -S boost fmt spdlog nlohmann-json

# .NET
sudo pacman -S dotnet-sdk dotnet-runtime
```

---

<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="32">
  <br>
  <a href="https://github.com/inzexg-coder">@inzexg-coder</a>
</p>
