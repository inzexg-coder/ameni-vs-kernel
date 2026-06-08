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
  Полное пошаговое руководство по исправлению ошибок линковки<br>
  LNK2019, LNK1104, LNK1120 и восстановлению Visual Studio C++ сборки.
</p>

<p align="center">
  <a href="#установка">Установка</a> &middot;
  <a href="#план-исправления">План исправления</a> &middot;
  <a href="#cli-агент">CLI агент</a> &middot;
  <a href="#архитектура">Архитектура</a>
</p>

<br>

---

## Установка

### Шаг A — Клонирование репозитория

Выберите вашу операционную систему и выполните команды.

**Arch Linux:**
```bash
sudo pacman -S git           # если git ещё не установлен
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
export PATH="$PATH:$(pwd)/.ameni/bin"
ameni vs about
```

Если команда `ameni vs about` вывела информацию об агенте — установка завершена.

**Windows (Git Bash / WSL):**
```bash
# Откройте Git Bash (или WSL)
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
export PATH="$PATH:$(pwd)/.ameni/bin"
ameni vs about
```

**Windows (PowerShell, без Git Bash):**
```powershell
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
.\ameni\bin\ameni.ps1 about
```

### Шаг B — Установка зависимостей для CLI

**Arch Linux (опционально — для полной диагностики):**
```bash
sudo pacman -S powershell       # чтобы запускать .ps1 скрипты
sudo pacman -S dotnet-sdk       # .NET SDK
```

**Windows (обязательно — для VS диагностики):**
```powershell
# PowerShell Core
winget install Microsoft.PowerShell
# или скачайте с https://github.com/PowerShell/PowerShell
```

### Шаг C — Проверка, что всё готово

```bash
ameni vs help
```

Эта команда покажет все доступные команды. Вы должны увидеть: `diagnose`, `check`, `props`, `errors`, `about`, `help`.

Если команда не найдена — проверьте, что вы добавили `.ameni/bin` в PATH или используйте полный путь:
```bash
./.ameni/bin/ameni vs help        # если вы в корне репозитория
```

Для PowerShell:
```powershell
.\ameni\bin\ameni.ps1 help
```

---

## План исправления

Если Visual Studio выдаёт ошибки LNK1120, LNK2019 или LNK1104 — не паникуйте. Следуйте плану строго по порядку. Каждый шаг либо исправляет проблему, либо говорит, что делать дальше.

<br>

### Шаг 1 — Диагностика окружения

**Цель:** понять, какие компоненты Visual Studio установлены, а каких не хватает.

**Что делает:** проверяет наличие VS, Windows SDK, MSVC toolchain и ключевых библиотек (kernel32.lib, vcruntime.lib).

**Arch Linux:**
```bash
ameni vs diagnose
```
Вывод сообщит, какие инструменты доступны (dotnet, mono, pwsh, gcc, cmake). Если вы не собираетесь чинить VS напрямую — переходите к Шагу 2 (сверка конфигурации).

**Windows (Git Bash / WSL):**
```bash
ameni vs diagnose
```
Скрипт запустит проверку через PowerShell. Вывод будет выглядеть так:

```
=== Environment Diagnostics ===
OS: MINGW64_NT-10.0 (x86_64)

=== Visual Studio Environment Verification ===
[OK] vswhere.exe найден
     Установка: Visual Studio Community 2022 [17.x]
[OK] Windows Kits найден
     SDK 10.0.19041.0: kernel32.lib найден
[OK] MSVC 14.35 (VS 2022 Community)
     vcruntime.lib найден
```

**Windows (PowerShell):**
```powershell
.\ameni\bin\ameni.ps1 diagnose
```

**Что искать в выводе:**
- `[OK]` — компонент найден, всё в порядке
- `[WARN]` — компонент не найден, но это может быть нормально
- `[ERROR]` — компонент отсутствует, это требует исправления

**Если есть ошибки — что делать:**
1. Запомните, чего не хватает (например, kernel32.lib или MSVC)
2. Переходите к Шагу 6 (переустановка SDK/VS)
3. Либо воспользуйтесь файлом `.vsconfig` для установки компонентов

**Если всё `[OK]` — переходите к Шагу 2.**

<br>

### Шаг 2 — Сравнение проекта с эталоном

**Цель:** проверить, совпадают ли пути VC++ Directories вашего проекта с правильными.

**Что делает:** читает ваш .vcxproj файл и сравнивает LibraryDirectories, IncludeDirectories и ExecutableDirectories с эталонными значениями.

**Windows (PowerShell):**
```powershell
pwsh ./scripts/diff-project-settings.ps1 -ProjectPath "C:\Users\ВашеИмя\Documents\MyProject\MyProject.vcxproj"
```

**Или через CLI:**
```bash
ameni vs check /path/to/project
```

**Ожидаемый вывод (всё хорошо):**
```
=== Diff: проект vs эталон ===
Файл: C:\MyProject\MyProject.vcxproj

  [OK] ExecutableDirectories
  [OK] IncludeDirectories
  [OK] LibraryDirectories
  [OK] LibraryWinRTDirectories
  [OK] SourceDirectories

Все настройки совпадают с эталоном.
```

**Ожидаемый вывод (есть проблемы):**
```
  [!] LibraryDirectories
      Сейчас:   $(VC_LibraryPath_x64);C:\Custom\Lib
      Эталон:  $(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64
```

**Что означает расхождение:** пути в вашем проекте были изменены (возможно, случайно), и компилятор не может найти нужные библиотеки.

**Что делать:**
- Если есть расхождения — переходите к Шагу 3
- Если совпадает, но ошибка остаётся — переходите к Шагу 6

<br>

### Шаг 3 — Применение эталонных путей через Property Sheet (безопасно)

**Цель:** исправить пути, НЕ изменяя ваш .vcxproj файл. Это самый безопасный метод — вы всегда можете отключить property sheet.

**Что делает:** файлы из папки `props/` — это готовые Property Sheets. Импортируйте их в Visual Studio, и они переопределят пути.

**Пошаговая инструкция:**
1. Откройте ваш проект в **Visual Studio**
2. В меню выберите **View → Property Manager** (если не видите — ищите через Ctrl+Q)
3. В окне Property Manager раскройте вашу конфигурацию (например, Debug | x64)
4. Кликните **правой кнопкой** на конфигурации
5. Выберите **Add Existing Property Sheet...**
6. Найдите в репозитории файл `props/DefaultPaths.props`
7. Нажмите **Open**

**Дополнительные property sheets (если нужно):**
- `props/DLL.props` — для проектов, собираемых как DLL
- `props/StaticLib.props` — для статических библиотек
- `props/DebugSettings.props` — для отладочных настроек
- `props/AdvancedSettings.props` — дополнительные параметры C/C++

**После импорта:**
```bash
# Запустите проверку снова — пути должны совпасть
pwsh ./scripts/diff-project-settings.ps1 -ProjectPath "путь\к\вашему\проекту.vcxproj"
```

**Если ошибки не исчезли — переходите к Шагу 4.**

**Как откатить:**
1. Откройте Property Manager
2. Кликните правой кнопкой на добавленном .props файле
3. Выберите **Remove**

<br>

### Шаг 4 — Автоматическое исправление .vcxproj скриптом

**Цель:** автоматически изменить все .vcxproj файлы в папке проекта, записав эталонные пути напрямую в XML.

**ВНИМАНИЕ:** скрипт изменяет файлы проектов. Он создаёт резервные копии (.bak), но всё равно будьте осторожны.

**Команда:**
```powershell
pwsh ./scripts/apply-default-paths.ps1 -Path "C:\Users\ВашеИмя\Documents\MyProject" -Architecture x64 -Backup $true
```

**Параметры:**
| Параметр | Что делает | Обязательный | Значение по умолчанию |
|----------|-----------|-------------|----------------------|
| `-Path` | Путь к папке с .vcxproj файлами | Нет | `.` (текущая папка) |
| `-Architecture` | Архитектура: x64, x86 или ARM64 | Нет | x64 |
| `-Backup` | Создавать .bak файлы | Нет | $true |

**Ожидаемый вывод:**
```
Найдено проектов: 3
Обработка: MyProject.vcxproj
  -> Бэкап: MyProject.vcxproj.bak
  [OK] LibraryDirectories -> эталон
  [OK] IncludeDirectories -> эталон
  [OK] ExecutableDirectories -> эталон
Обработка: MyProject.Tests.vcxproj
  [OK] LibraryDirectories -> эталон
  ...

Готово! Пути обновлены для архитектуры x64.
Для отката используйте .bak файлы.
```

**Как откатить:**
```powershell
# Просто переименуйте .bak обратно
Rename-Item "MyProject.vcxproj.bak" "MyProject.vcxproj"
```

**Если ошибки остались — переходите к Шагу 5.**

<br>

### Шаг 5 — Ручное редактирование

**Цель:** вручную проверить и исправить настройки через интерфейс Visual Studio.

**Пошаговая инструкция:**
1. Кликните **правой кнопкой** на проекте в Solution Explorer
2. Выберите **Properties**
3. Перейдите в **Configuration Properties → VC++ Directories**
4. Сверьте каждое поле с эталоном:

| Поле | Эталонное значение |
|------|-------------------|
| Executable Directories | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |
| Include Directories | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| Library Directories | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |
| Source Directories | `$(VC_SourcePath);` |

**Как понять, что нужно менять:**
- Если в Library Directories нет `$(VC_LibraryPath_x64)` — это почти гарантированная причина LNK2019
- Если там указан жёсткий путь типа `C:\Custom\Lib` — замените на эталонный
- Не удаляйте существующие пути — просто добавьте эталонные в начало

**Если после ручной правки проблема не ушла — переходите к Шагу 6.**

<br>

### Шаг 6 — Переустановка SDK или Visual Studio

**Цель:** переустановить недостающие компоненты Windows SDK или MSVC toolchain.

**Способ 1 — Через .vsconfig (рекомендуется):**
1. Откройте **Visual Studio Installer**
2. Нажмите **Изменить** на вашей версии VS
3. Перейдите на вкладку **Импорт**
4. Выберите `.vsconfig` из этого репозитория
5. Нажмите **Импорт** → **Установить**

Файл `.vsconfig` выберет:
- Рабочую нагрузку "Desktop development with C++"
- MSVC v141, v143, v144 (для VS 2017, 2022, 2025)
- Windows 10 SDK (10.0.19041.0) и Windows 11 SDK (10.0.22621.0)
- ATL, MFC, CMake, Clang/LLVM

**Способ 2 — Вручную:**
1. Откройте **Visual Studio Installer**
2. Нажмите **Изменить**
3. Убедитесь, что выбраны:
   - Desktop development with C++
   - Windows 10/11 SDK
   - MSVC v143 (или ваша версия)
4. Нажмите **Установить**

**Способ 3 — Чистая переустановка:**
```
1. Панель управления → Программы и компоненты
2. Найдите "Windows Software Development Kit"
3. Кликните правой кнопкой → Изменить → Удалить
4. Установите заново через Visual Studio Installer
```

**Arch Linux (альтернативный подход — используйте dotnet):**
```bash
sudo pacman -S dotnet-sdk       # для .NET проектов
sudo pacman -S mono             # для .NET Framework
sudo pacman -S wine             # для запуска VS (ограниченно)
```

Если после переустановки ошибка остаётся — повторите план с Шага 1, но теперь проблема может быть в коде проекта (например, пропущенные header-файлы или неверные #pragma comment).

---

## Справочник Property Sheets

Файлы в папке `props/` — готовые конфигурации для импорта в Visual Studio.

| Файл | Когда использовать | Что делает |
|------|-------------------|------------|
| `DefaultPaths.props` | Всегда, для x64 проектов | Исправляет VC++ Directories на эталонные |
| `DefaultPaths-x86.props` | Если собираете под x86 | То же, но для 32-битных проектов |
| `DefaultPaths-ARM64.props` | Если собираете под ARM64 | Пути для ARM64 |
| `AdvancedSettings.props` | Для тонкой настройки C/C++ | Дополнительные опции компилятора |
| `DLL.props` | Для DLL проектов | Настройки экспорта и линковки DLL |
| `StaticLib.props` | Для статических библиотек | Настройки lib-проектов |
| `DebugSettings.props` | Для отладки | Символы, PDB, оптимизация |
| `Driver.props` | Для драйверов | WDK-специфичные настройки |

### Как добавить Property Sheet

1. **Visual Studio:** View → Property Manager → Правый клик на конфигурации → Add Existing Property Sheet → выберите .props файл
2. **Вручную:** добавьте в .vcxproj:
   ```xml
   <Import Project="путь\к\DefaultPaths.props" />
   ```

---

## Справочник ошибок линковки

Каждый файл в папке `errors/` содержит: описание ошибки, типичные причины, пошаговое решение, примеры диагностики.

| Ошибка | Симптом | Причина | Что делать |
|--------|---------|---------|------------|
| **LNK1104** | `cannot open file 'kernel32.lib'` | SDK не установлен или пути сбиты | Шаг 3 или Шаг 6 |
| **LNK2019** | `unresolved external symbol _WinMain@16` | Неправильные Library Directories | Шаг 2 → Шаг 3 |
| **LNK2001** | `unresolved external symbol _main` | Неверный /SUBSYSTEM | Шаг 5 (проверить subsystem) |
| **LNK1120** | `1 unresolved externals` | Следствие LNK2019/2001/1104 | Смотреть первопричину |

```bash
# Просмотр описания конкретной ошибки
ameni vs errors lnk1104-cannot-open-file
```

---

## Конфигурации по версиям Visual Studio

В папках `vs2017/`, `vs2022/`, `vs2025/` находятся конфигурации, адаптированные под конкретные версии.

| Папка | Версия VS | Platform Toolset | MSVC версия |
|-------|-----------|------------------|-------------|
| `vs2017/` | Visual Studio 2017 | v141 | 14.1x |
| `vs2022/` | Visual Studio 2022 | v143 | 14.3x |
| `vs2025/` | Visual Studio 2025 | v144 | 14.4x |

В каждой папке:
- `general.md` — общие настройки проекта
- `vc++-directories.md` — специфичные для версии VC++ Directory пути

---

## Скрипты

Все скрипты в папке `scripts/` написаны на PowerShell и запускаются на обеих платформах.

| Скрипт | Команда | Что делает |
|--------|---------|------------|
| `verify-environment.ps1` | `pwsh scripts/verify-environment.ps1` | Проверяет VS, SDK, MSVC |
| `diff-project-settings.ps1` | `pwsh scripts/diff-project-settings.ps1 -ProjectPath "..."` | Сравнивает .vcxproj с эталоном |
| `apply-default-paths.ps1` | `pwsh scripts/apply-default-paths.ps1 -Path "..."` | Автоматически исправляет пути |

**Arch Linux:**
```bash
sudo pacman -S powershell
pwsh ./scripts/verify-environment.ps1
```

**Windows (PowerShell):**
```powershell
pwsh ./scripts/verify-environment.ps1
```

---

## CLI агент

Все команды `ameni vs` доступны на обеих платформах.

### ameni vs diagnose

**Arch Linux:**
```bash
ameni vs diagnose

=== Environment Diagnostics ===
OS: Linux (x86_64)
[INFO]  dotnet: 9.0.201
[INFO]  mono: Mono JIT compiler version 6.12.0
[INFO]  pwsh: PowerShell 7.4.0

=== Build Tools ===
[INFO]  gcc: gcc (GCC) 14.2.0
[INFO]  g++: g++ (GCC) 14.2.0
[INFO]  make: GNU Make 4.4.1
[INFO]  cmake: cmake version 3.30.0
[INFO]  clang: clang version 18.0.0
```

**Windows (Git Bash):**
```bash
ameni vs diagnose
# автоматически запускает pwsh ./scripts/verify-environment.ps1
```

**Windows (PowerShell):**
```powershell
.\ameni\bin\ameni.ps1 diagnose
```

### ameni vs check

```bash
ameni vs check ./MyProject
```

Проверяет .vcxproj файлы на нестандартные пути LibraryDirectories.

### ameni vs props

```bash
ameni vs props
```

Показывает список всех доступных Property Sheets с краткими описаниями.

### ameni vs errors

```bash
ameni vs errors                  # список всех ошибок
ameni vs errors lnk1104-cannot-open-file  # описание конкретной ошибки
```

### ameni vs help / about

```bash
ameni vs help                    # полный мануал
ameni vs about                   # краткая информация
```

---

## Архитектура репозитория

```
ameni-vs-kernel/
  .ameni/
    assets/          - логотип
    bin/
      ameni          - CLI агент (bash, кроссплатформенный)
      ameni.ps1      - CLI агент (PowerShell, Windows)
  props/             - Property Sheets для импорта
  scripts/           - PowerShell скрипты диагностики
  errors/            - документация по ошибкам линковки
  vs2017/            - конфигурации для VS 2017
  vs2022/            - конфигурации для VS 2022
  vs2025/            - конфигурации для VS 2025
  .vsconfig          - манифест компонентов VS Installer
  PKGBUILD           - для сборки на Arch Linux
```

---

<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="32">
  <br>
  <a href="https://github.com/inzexg-coder">@inzexg-coder</a>
</p>
