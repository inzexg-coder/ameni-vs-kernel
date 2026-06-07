<p align="center">
  <img src="https://img.shields.io/badge/Visual%20Studio-Configuration%20Archive-blue?logo=visualstudio">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey">
</p>

<br>

<h1 align="center">Visual Studio Configuration Archive</h1>

<p align="center">
  Пошаговое руководство по исправлению ошибок линковки (kernel32.lib, LNK2019, LNK1104) и восстановлению настроек проектов VS
</p>

---

## 📖 Содержание
- [Быстрый старт](#быстрый-старт)
- [Пошаговое устранение неполадок](#пошаговое-устранение-неполадок)
- [Эталонная конфигурация](#эталонная-конфигурация)
- [Property Sheets (.props)](#propertysheets-props)
- [PowerShell‑скрипты](#powershell-скрипты)
- [Конфиги по версиям VS](#конфиги-по-версиям-vs)
- [Справочник ошибок линковки](#справочник-ошибок-линковки)
- [.vsconfig — манифест компонентов VS](#vsconfig---манифест-компонентов-vs)

---

## 🚀 Быстрый старт

Если сборка падает с ошибками `LNK1120`, `LNK2019` или `LNK1104`, следуйте этим шагам **по порядку** — от самых простых и безопасных к более сложным/рискованным.

| Шаг | Действие | Описание |
|-----|----------|----------|
| 1 | 🔍 **Диагностика окружения** | Проверить установку VS, Windows SDK, MSVC toolchain и наличие `kernel32.lib` |
| 2 | 📊 **Сравнение с эталоном** | Сверить текущие настройки .vcxproj с эталонными из репозитория |
| 3 | 🛠️ **Применить эталон через .props** (рекомендуется) | Импортировать property sheet для исправления VC++ Directories без редактирования .vcxproj |
| 4 | ⚙️ **Применить эталон через скрипт** | Автоматически исправить все .vcxproj в папке |
| 5 | 🔧 **Ручное редактирование** | Открыть свойства проекта и исправить пути вручную |
| 6 | 💾 **Переустановка SDK/VS** | Переустановить или восстановить Windows SDK или инструменты сборки VS |

---

## 🛠️ Пошаговое устранение неполадок

### Шаг 1 — Диагностика окружения

Запустите скрипт проверки, чтобы убедиться, что инструменты сборки установлены и `kernel32.lib` доступен.

**PowerShell:**
```powershell
# Из корня репозитория:
.\scripts\verify-environment.ps1
```

**Что проверяет:**
- Наличие `vswhere.exe` → установки VS
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

Если скрипт сообщает о недостающих компонентах → переходите к **Шагу 6** (переустановка) или используйте `.vsconfig` для их установки.

---

### Шаг 2 — Сравнение с эталоном

Запустите скрипт сравнения, чтобы увидеть, какие свойства VC++ Directories отличаются от эталонных.

**PowerShell:**
```powershell
# Укажите полный путь к вашему .vcxproj
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

Если все пункты показывают `[OK]` → ваши VC++ Directories уже совпадают с эталоном; проблема может быть в другом (см. справочник ошибок ниже).

---

### Шаг 3 — Применение эталонного через .props (рекомендуется)

Property Sheets позволяют применять эталонные настройки без изменения .vcxproj файла. Это самый безопасный и обратимый способ.

**Как сделать:**
1. В Visual Studio откройте **Вид → Другие окна → Диспетчер свойств**
2. Правый клик по конфигурации (например `Debug|x64`) → **Добавить существующий лист свойств…**
3. Перейдите в репозиторий и выберите:
   - `props/DefaultPaths.props` для проектов x64
   - `props/DefaultPaths-x86.props` для проектов x86
   - `props/DefaultPaths-ARM64.props` для проектов ARM64
4. Нажмите **OK**, затем **Перестроить** решение.

**Как отменить:**
Просто удалите лист свойств из Диспетчера свойств — изменений в .vcxproj не останется.

---

### Шаг 4 — Применение эталонного через скрипт

Используйте, когда нужно поправить много проектов сразу или предпочитаете полностью автоматизированный подход. Скрипт создаёт `.bak` копии перед изменением.

**PowerShell:**
```powershell
# Исправить все .vcxproj в текущей папке (по умолчанию)
.\scripts\apply-default-paths.ps1

# Указать папку и архитектуру явно
.\scripts\apply-default-paths.ps1 -Path "C:\SolutionRoot" -Architecture x64

# Не создавать бэкапы (не рекомендуется)
.\scripts\apply-default-paths.ps1 -Backup $false
```

**Что делает скрипт:**
- Рекурсивно ищет все файлы `*.vcxproj`
- Для каждого файла:
  1. Создаёт `<file>.vcxproj.bak` (если `-Backup $true`)
  2. Заменяет `LibraryDirectories`, `IncludeDirectories`, `ExecutableDirectories` на эталонные значения для выбранной архитектуры
  3. Сохраняет файл

**Как откатить:**
Переименуйте каждый `.bak` файл обратно в `.vcxproj` или удалите изменённые файлы и восстановите их из системы контроля версий.

---

### Шаг 5 — Ручное редактирование

Применяйте только если предыдущие шаги не помогли или нужно отредактировать одну настройку.

**Где сделать:**
1. Правый клик по проекту → **Свойства**
2. Перейдите в **Свойства конфигурации → VC++ Directories**
3. Отредактируйте следующие поля (значения зависят от архитектуры):

| Свойство | Значение для x64 |
|----------|------------------|
| **Library Directories** | `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64` |
| **Include Directories** | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` |
| **Executable Directories** | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` |

4. Нажмите **OK** → **Перестроить**.

**Совет:** Сохраните копию исходных значений перед изменением, чтобы можно было откатиться.

---

### Шаг 6 — Переустановка SDK / Visual Studio

Используйте только если диагностика показывает, что файлы отсутствуют или повреждены.

**Переустановка Windows SDK:**
1. Откройте **Visual Studio Installer**
2. Нажмите **Изменить** у вашего экземпляра VS
3. Перейдите на вкладку **Отдельные компоненты**
4. Найдите и отметьте:
   - `Windows 10 SDK (10.0.19041.0)` или последнюю версию
   - `Windows 11 SDK (10.0.22621.0)` (если используете VS 2022+)
5. Нажмите **Изменить** для установки

**Восстановление инструментов сборки Visual Studio:**
В том же установщике выберите **Восстановить** вместо **Изменить**.

**Альтернатива — использование .vsconfig:**
Файл `.vsconfig` в корне репозитория содержит точный список необходимых компонентов для нативной разработки на C++. Импортируйте его через **Изменить → Импорт** в Visual Studio Installer, чтобы получить согласованный набор.

---

## 📚 Эталонная конфигурация

Файлы в корне репозитория описывают точные эталонные значения для наиболее важных групп свойств проекта — те настройки, которые VS выставляет по умолчанию при чистой установке.

| Файл | Описание |
|------|----------|
| `vc++-directories.md` | **VC++ Directories** — контролирует, где компатор/линковщик ищут заголовки, библиотеки и инструменты. Запись `Library Directories` является ключом для исправления `kernel32.lib`. |
| `general.md` | **Общие свойства** — выходные каталоги, промежуточный каталог, платформенный набор инструментов, версия Windows SDK, тип конфигурации. |
| `advanced.md` | **Дополнительные свойства** — использование отладочных библиотек, набор символов, оптимизация całej программы, MFC, настройки C++/CLI. |
| `debugging.md` | **Настройки отладчика** — рабочий каталог, тип отладчика, переменные окружения, ускоритель для C++ AMP. |

Эти файлы предназначены для **справочного использования** — сравнивайте их с настройками вашего проекта или применяйте через предоставленные `.props` файлы/скрипты.

---

## 🧩 Property Sheets (.props)

Property Sheets — это MSBuild XML‑файлы, которые можно подключать к любому `.vcxproj` через **Диспетчер свойств**. Они применяют настройки без изменения самого файла проекта.

| Файл | Платформа | Назначение |
|------|-----------|------------|
| `props/DefaultPaths.props` | x64 | Эталонные VC++ Directories (наиболее распространённый) |
| `props/DefaultPaths-x86.props` | x86 | Эталонные VC++ Directories для 32‑битных проектов |
| `props/DefaultPaths-ARM64.props` | ARM64 | Эталонные VC++ Directories для проектов ARM64 |
| `props/DebugSettings.props` | любая | Эталонные настройки отладчика |
| `props/AdvancedSettings.props` | любая | Эталонные дополнительные + C++/CLI свойства |
| `props/DLL.props` | x64 | Минимальная настройка для динамической библиотеки (.dll) |
| `props/StaticLib.props` | x64 | Минимальная настройка для статической библиотеки (.lib) |
| `props/Driver.props` | x64 | Минимальная настройка для ядерного драйвера (.sys) |

### Пример содержимого .props (DefaultPaths.props)
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

## ⚙️ PowerShell‑скрипты

Папка `scripts/` содержит три утилиты для диагностики и исправления конфигураций проектов VS.

| Скрипт | Что делает | Параметры |
|--------|------------|-----------|
| `scripts/verify-environment.ps1` | Проверяет установку VS, Windows SDK, MSVC и наличие `kernel32.lib` | Нет |
| `scripts/diff-project-settings.ps1` | Сравнивает `.vcxproj` с эталонными VC++ Directories | `-ProjectPath <string>` (обязательно) |
| `scripts/apply-default-paths.ps1` | Применяет эталонные пути ко всем `.vcxproj` в папке | `-Path <string>` (по умолчанию `.`)<br>`-Architecture <x64\|x86\|ARM64>` (по умолчанию `x64`)<br>`-Backup <bool>` (по умолчанию `$true`) |

Все скрипты **без комментариев** — оставлен только исполняемый код и определения параметров.

---

## 🏷️ Конфиги по версиям VS

Разные версии Visual Studio используют разные Platform Toolset и могут иметь небольшие различия в путях.

| Папка | Версия VS | Platform Toolset | Примечания |
|-------|-----------|------------------|------------|
| `vs2017/` | Visual Studio 2017 | v141 | MSVC 14.1x, Windows Kits\10 |
| `vs2022/` | Visual Studio 2022 | v143 | MSVC 14.3x — точно совпадает с корневым эталоном |
| `vs2025/` | Visual Studio 2025 | v144 | MSVC 14.4x — может использовать Windows SDK 11.0 |

В каждой папке версии находятся файлы `general.md` и `vc++-directories.md`, адаптированные под соответствующий toolset.

---

## 🔗 Справочник ошибок линковки

Папка `errors/` содержит подробные объяснения распространённых ошибок линковки, их симптомов, причин и способов решения.

| Файл | Ошибка | Типичные симптомы | Быстрое решение |
|------|--------|-------------------|-----------------|
| `errors/lnk1104-cannot-open-file.md` | **LNK1104** | `fatal error LNK1104: cannot open file 'kernel32.lib'` | Восстановить Library Directories или переустановить Windows SDK |
| `errors/lnk2019-unresolved-external.md` | **LNK2019** | `error LNK2019: unresolved external symbol _WinMain@16` | Проверить Library Directories и Additional Dependencies |
| `errors/lnk2001-unresolved-external.md` | **LNK2001** | `LNK2001: unresolved external symbol _main` | Проверить /SUBSYSTEM соответствует точке входа (console vs windows) |
| `errors/lnk1120-link-failed.md` | **LNK1120** | `fatal error LNK1120: 1 unresolved externals` | Посмотреть на первопричину в LNK2019/2001/1104 |

В каждом файле:
- Краткое описание ошибки
- Типичные причины
- Пошаговые инструкции по устранению
- Примечания о том, когда следует переходить к следующему шагу диагностики

---

## 🧩 .vsconfig — манифест компонентов VS

Файл `.vsconfig` в корне репозитория указывает **Visual Studio Installer**, какие компоненты установить для разработки нативного C++.

### Как использовать
1. Откройте **Visual Studio Installer**
2. Нажмите **Изменить** у вашего экземпляра VS
3. Выберите вкладку **Импорт**
4. Найдите и выберите `.vsconfig` из этого репозитория
5. Нажмите **Установить** (или **Обновить**) для применения списка компонентов

### Что включает
Манифест выбирает:
- **Нагрузка**: `Рабочий стол с C++`
- **Отдельные компоненты**:
  - Наборы инструментов MSVC v141 и v143 (x86, x64, ARM64)
  - Windows 10 SDK (10.0.19041.0) и Windows 11 SDK (10.0.22621.0)
  - CMake, ATL, MFC, Clang/LLVM для Windows
  - MSBuild и связанные инструменты сборки

Использование `.vsconfig` гарантирует, что у вас установлены именно те наборы инструментов и SDK, которые соответствуют эталонным конфигурациям в этом репозитории.

---

## 📄 Лицензия

Этот репозиторий предоставляет только конфигурационные файлы и документацию.  
Бинарные файлы, установщики и проприетарный код не включены.  
Вы можете свободно использовать, копировать и изменять файлы для своих проектов.

