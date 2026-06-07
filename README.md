# Visual Studio Configuration Archive

Документированный архив эталонных конфигураций Visual Studio для восстановления
проектных настроек, устранения ошибок линковки (`kernel32.lib`, `LNK2019`, `LNK1104`)
и диагностики сборочного окружения.

---

## Содержание

- [Назначение](#Назначение)
- [Структура репозитория](#Структура-репозитория)
- [.props — Property Sheets для импорта в проект](#props--property-sheets-для-импорта-в-проект)
  - [DefaultPaths.props / -x86 / -ARM64](#defaultpathsprops--x86---arm64)
  - [DebugSettings.props](#debugsettingsprops)
  - [AdvancedSettings.props](#advancedsettingsprops)
  - [DLL.props / StaticLib.props / Driver.props](#dllprops--staticlibprops--driverprops)
- [Scripts — PowerShell-скрипты](#scripts--powershell-скрипты)
  - [verify-environment.ps1](#verify-environmentps1)
  - [diff-project-settings.ps1](#diff-project-settingsps1)
  - [apply-default-paths.ps1](#apply-default-pathssp1)
- [Версии Visual Studio](#Версии-visual-studio)
  - [vs2017 (v141)](#vs2017-v141)
  - [vs2022 (v143)](#vs2022-v143)
  - [vs2025 (v144)](#vs2025-v144)
- [Errors — справочник ошибок линковки](#errors--справочник-ошибок-линковки)
  - [LNK1104 — Cannot Open File](#lnk1104--cannot-open-file)
  - [LNK2019 — Unresolved External Symbol](#lnk2019--unresolved-external-symbol)
  - [LNK2001 — Unresolved External (Subsystem)](#lnk2001--unresolved-external-subsystem)
  - [LNK1120 — Link Failed Summary](#lnk1120--link-failed-summary)
- [.vsconfig — установка компонентов VS](#vsconfig--установка-компонентов-vs)
- [Быстрый старт](#Быстрый-старт)
- [Типовой сценарий: kernel32.lib](#Типовой-сценарий-kernel32lib)
- [Поддержка](#Поддержка)

---

## Назначение

При длительной работе с Visual Studio проектные настройки — в особенности пути к
библиотекам и заголовочным файлам — могут сбиваться из-за:

- обновления Windows SDK или Visual Studio;
- импорта конфигураций из других проектов или решений;
- ручного редактирования `.vcxproj` / `.props` файлов;
- повреждения глобальных конфигураций VS.

Наиболее частая проблема — ошибка `LNK1120: 1 unresolved externals` с корнем
`kernel32.lib`. Она означает, что линковщик не может найти одну из фундаментальных
системных библиотек Windows.

Этот репозиторий предоставляет **эталонные, проверенные настройки**,
которые можно применить тремя способами:

1. **Импортировать `.props` файл** через Property Manager (рекомендуется).
2. **Пропустить PowerShell-скрипт** автоматического восстановления.
3. **Сверить вручную** текущие пути с эталонными по документации.

---

## Структура репозитория

```
visual-studio-fixing/
│
├── props/                          # Property sheets (.props) — подключение через Property Manager
│   ├── DefaultPaths.props          #   Эталонные пути VC++ Directories (x64)
│   ├── DefaultPaths-x86.props      #   Эталонные пути VC++ Directories (x86)
│   ├── DefaultPaths-ARM64.props    #   Эталонные пути VC++ Directories (ARM64)
│   ├── DebugSettings.props         #   Настройки отладчика (Working Directory, Debugger Type и др.)
│   ├── AdvancedSettings.props      #   Advanced + C++/CLI свойства (Whole Program Optimization, MFC и др.)
│   ├── DLL.props                   #   Базовые настройки для Dynamic Library (.dll)
│   ├── StaticLib.props             #   Базовые настройки для Static Library (.lib)
│   └── Driver.props                #   Базовые настройки для Kernel Driver (.sys)
│
├── scripts/                        # PowerShell-скрипты для диагностики и восстановления
│   ├── verify-environment.ps1      #   Проверка установки VS, Windows SDK, MSVC, наличия kernel32.lib
│   ├── diff-project-settings.ps1   #   Сравнение текущих .vcxproj настроек с эталоном
│   └── apply-default-paths.ps1     #   Автоматическое обновление путей в .vcxproj файлах
│
├── vs2017/                         # Конфигурации для Visual Studio 2017 (Platform Toolset v141)
│   ├── general.md                  #   General Properties
│   └── vc++-directories.md         #   VC++ Directories
│
├── vs2022/                         # Конфигурации для Visual Studio 2022 (Platform Toolset v143)
│   ├── general.md                  #   General Properties
│   └── vc++-directories.md         #   VC++ Directories
│
├── vs2025/                         # Конфигурации для Visual Studio 2025 (Platform Toolset v144)
│   ├── general.md                  #   General Properties
│   └── vc++-directories.md         #   VC++ Directories
│
├── errors/                         # Описание типичных ошибок линковки и их решений
│   ├── lnk1104-cannot-open-file.md #   LNK1104 — файл библиотеки не найден
│   ├── lnk1120-link-failed.md      #   LNK1120 — итоговая ошибка, ссылка на первопричину
│   ├── lnk2001-unresolved-external.md # LNK2001 — неверный SUBSYSTEM / entry point
│   └── lnk2019-unresolved-external.md # LNK2019 — неразрешённый внешний символ
│
├── .vsconfig                       # Манифест для Visual Studio Installer (импорт компонентов)
│
├── README.md                       # Документация (этот файл)
├── general.md                      # General Properties — эталон
├── advanced.md                     # Advanced Properties — эталон
├── debugging.md                    # Debugger Settings — эталон
└── vc++-directories.md             # VC++ Directories — эталон
```

---

## .props — Property Sheets для импорта в проект

Property sheets — это файлы в формате XML (MSBuild), которые можно подключить к любому
`.vcxproj` через **Property Manager** (`View → Other Windows → Property Manager`).
Подключение происходит для выбранной конфигурации (Debug/Release, x64/x86/ARM64).

После импорта все свойства из `.props` автоматически применяются при сборке.
Их можно отключить, просто удалив лист из Property Manager — никаких изменений
в самом `.vcxproj` не останется.

### DefaultPaths.props / -x86 / -ARM64

**Назначение:** устанавливает эталонные пути VC++ Directories для разрешения
`kernel32.lib` и других системных библиотек.

**Содержит следующие свойства:**

| Свойство | x64 | x86 | ARM64 |
|---|---|---|---|
| `ExecutableDirectories` | `$(VC_ExecutablePath_x64);$(CommonExecutablePath)` | `$(VC_ExecutablePath_x86);$(CommonExecutablePath)` | `$(VC_ExecutablePath_ARM64);$(CommonExecutablePath)` |
| `IncludeDirectories` | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` | (то же) | (то же) |
| `ExternalIncludeDirectories` | `$(VC_IncludePath);$(WindowsSDK_IncludePath);` | (то же) | (то же) |
| `ReferenceDirectories` | `$(VC_ReferencesPath_x64);` | `$(VC_ReferencesPath_x86);` | `$(VC_ReferencesPath_ARM64);` |
| **`LibraryDirectories`** | **`$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64`** | **`$(VC_LibraryPath_x86);$(WindowsSDK_LibraryPath_x86);$(NETFXKitsDir)Lib\um\x86`** | **`$(VC_LibraryPath_ARM64);$(WindowsSDK_LibraryPath_ARM64);$(NETFXKitsDir)Lib\um\arm64`** |
| `LibraryWinRTDirectories` | `$(WindowsSDK_MetadataPath);` | (то же) | (то же) |
| `SourceDirectories` | `$(VC_SourcePath);` | (то же) | (то же) |
| `ExcludeDirectories` | `$(VC_SourcePath);` | (то же) | (то же) |

**Критическая строка (LibraryDirectories):**
`$(NETFXKitsDir)Lib\um\x64` — это путь, где находится `kernel32.lib`.
`$(NETFXKitsDir)` раскрывается, например, в `C:\Program Files (x86)\Windows Kits\10\`.

### DebugSettings.props

**Назначение:** эталонные настройки отладчика.

| Свойство | Значение | Комментарий |
|---|---|---|
| `LocalDebuggerCommand` | `$(TargetPath)` | Запускать сам исполняемый файл |
| `LocalDebuggerWorkingDirectory` | `$(ProjectDir)` | Рабочий каталог — корень проекта |
| `LocalDebuggerAttach` | `No` | Запускать новый процесс |
| `LocalDebuggerDebuggerType` | `Auto` | Автоматический выбор отладчика |
| `LocalDebuggerMergeEnvironment` | `Yes` | Наследовать системные переменные |
| `LocalDebuggerSQLDebugging` | `No` | Отладка SQL отключена |
| `LocalDebuggerAMPDefaultAccelerator` | `WARP software accelerator` | C++ AMP — программный рендеринг |

### AdvancedSettings.props

**Назначение:** эталонные расширенные и C++/CLI свойства.

Ключевые свойства:

| Свойство | Значение | Значение |
|---|---|---|
| `UseDebugLibraries` | `Yes` | Использовать debug-версии runtime |
| `CharacterSet` | `Use Unicode Character Set` | Юникод (влияет на маппинг WinAPI) |
| `WholeProgramOptimization` | `NoWholeProgramOptimization` | Оптимизация отключена |
| `UseOfMfc` | `Use Standard Windows Libraries` | Стандартные библиотеки, не MFC |
| `CLRSupport` | `No` | Нативный C++, без .NET |
| `EnableUnitySupport` | `No` | Unity (Jumbo) сборка отключена |

### DLL.props / StaticLib.props / Driver.props

**Назначение:** минимальные настройки для разных типов проектов.

| Файл | `ConfigurationType` | `TargetExt` | Особенности |
|---|---|---|---|
| `DLL.props` | `DynamicLibrary` | `.dll` | Требует `/DLL` у линковщика |
| `StaticLib.props` | `StaticLibrary` | `.lib` | Не линкует `kernel32.lib` напрямую |
| `Driver.props` | `Driver` | `.sys` | Использует `ntoskrnl.lib` вместо `kernel32.lib` |

---

## Scripts — PowerShell-скрипты

### verify-environment.ps1

**Назначение:** диагностика сборочного окружения.

Скрипт последовательно проверяет:

1. **Наличие Visual Studio** — через `vswhere.exe` (расположение установок).
2. **Наличие Windows SDK** — поиск папки `Windows Kits\10` и `kernel32.lib`.
3. **Наличие MSVC Toolchain** — поиск директорий `MSVC\14.x\lib\x64` и проверка `vcruntime.lib`.
4. **Переменные окружения** — `VC_IncludePath`, `VC_LibraryPath_x64`, `WindowsSDK_IncludePath`,
   `WindowsSDK_LibraryPath_x64`, `NETFXKitsDir`, `VC_ExecutablePath_x64`.

**Пример вывода:**
```
=== Visual Studio Environment Verification ===

[OK] vswhere.exe найден
     Установка: Visual Studio Community 2022 [17.x]
[OK] Windows Kits найден
     SDK 10.0.19041.0: kernel32.lib найден
[OK] MSVC 14.35 (VS 2022 Community)
     vcruntime.lib найден
[OK] VC_IncludePath = C:\Program Files\Microsoft Visual Studio\...
```

**Использование:**
```powershell
.\scripts\verify-environment.ps1
```

### diff-project-settings.ps1

**Назначение:** сравнение текущих настроек `.vcxproj` с эталонными путями репозитория.

Скрипт:
- Читает `.vcxproj` как XML.
- Извлекает все свойства VC++ Directories.
- Сравнивает каждое с эталонным значением из репозитория.
- Выводит: `[OK]` — совпадает, `[!]` — отличается (показывает оба значения).

**Параметры:**

| Параметр | Обязательный | Описание |
|---|---|---|
| `-ProjectPath` | Да | Путь к `.vcxproj` файлу |

**Использование:**
```powershell
.\scripts\diff-project-settings.ps1 -ProjectPath "C:\MyProject\MyProject.vcxproj"
```

**Пример вывода:**
```
=== Diff: проект vs эталон ===
Файл: C:\MyProject\MyProject.vcxproj

  [OK] ExecutableDirectories
  [!] LibraryDirectories
      Сейчас:   $(VC_LibraryPath_x64);OTHER_INCLUDE
      Эталон:  $(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64
  [OK] IncludeDirectories
```

### apply-default-paths.ps1

**Назначение:** автоматическое восстановление эталонных путей во всех `.vcxproj`
файлах в указанной директории (рекурсивно).

**Параметры:**

| Параметр | Обязательный | По умолчанию | Описание |
|---|---|---|---|
| `-Path` | Нет | `.` | Путь к папке с проектами |
| `-Architecture` | Нет | `x64` | Целевая архитектура: `x64`, `x86` или `ARM64` |
| `-Backup` | Нет | `$true` | Создавать `.bak` копии перед изменением |

**Использование:**
```powershell
# Восстановить все проекты в текущей папке под x64
.\scripts\apply-default-paths.ps1

# Восстановить проекты в C:\Projects под x86
.\scripts\apply-default-paths.ps1 -Path "C:\Projects" -Architecture x86

# Восстановить без создания бэкапов
.\scripts\apply-default-paths.ps1 -Backup $false
```

**Что делает скрипт:**
1. Находит все файлы `*.vcxproj` рекурсивно.
2. Для каждого создаёт `.bak` (если `-Backup $true`).
3. Заменяет `LibraryDirectories`, `IncludeDirectories`, `ExecutableDirectories` на эталонные.
4. Сохраняет изменения.

---

## Версии Visual Studio

### vs2017 (v141)

**Папка:** `vs2017/`

Visual Studio 2017 использует Platform Toolset v141. Пути к MSVC toolchain:
```
C:\Program Files (x86)\Microsoft Visual Studio\2017\*\VC\Tools\MSVC\14.1*\lib\x64
```

Файлы:
- `general.md` — General Properties для VS 2017.
- `vc++-directories.md` — VC++ Directories с особенностями VS 2017.

### vs2022 (v143)

**Папка:** `vs2022/`

Visual Studio 2022 использует Platform Toolset v143.
Этот набор конфигураций полностью соответствует эталонным файлам в корне репозитория.

Файлы:
- `general.md` — General Properties для VS 2022.
- `vc++-directories.md` — VC++ Directories, дублирует корневой `vc++-directories.md`.

### vs2025 (v144)

**Папка:** `vs2025/`

Visual Studio 2025 использует Platform Toolset v144.

**Отличия от предыдущих версий:**
- MSVC toolchain: `...\Microsoft Visual Studio\2025\*\VC\Tools\MSVC\14.4*\lib\x64`.
- Может использовать Windows SDK 11.0 — тогда `kernel32.lib` может находиться
  по пути `...\Windows Kits\11\lib\<version>\um\x64`.
- Стандарт C++ по умолчанию может быть C++17 или C++20.

Файлы:
- `general.md` — General Properties для VS 2025.
- `vc++-directories.md` — VC++ Directories с особенностями VS 2025.

---

## Errors — справочник ошибок линковки

Папка `errors/` содержит подробное описание частых ошибок линковки,
их симптомов, причин и методов решения.

### LNK1104 — Cannot Open File

**Файл:** `errors/lnk1104-cannot-open-file.md`

**Симптом:**
```
fatal error LNK1104: cannot open file 'kernel32.lib'
```

**Причины:**
- `kernel32.lib` отсутствует — Windows SDK не установлен или повреждён.
- В Library Directories указан несуществующий путь.
- Файл заблокирован антивирусом.
- Несоответствие разрядности: проект x86, а путь указывает на x64.

**Решение:** восстановить пути через `DefaultPaths.props` или `apply-default-paths.ps1`.
Если файла физически нет — переустановить Windows SDK через Visual Studio Installer.

### LNK2019 — Unresolved External Symbol

**Файл:** `errors/lnk2019-unresolved-external.md`

**Симптом:**
```
error LNK2019: unresolved external symbol _WinMain@16 referenced in function
```

**Причины:**
- Отсутствует `kernel32.lib` в Library Directories.
- Пропущена библиотека в Linker → Input → Additional Dependencies (например, `ws2_32.lib`).
- Несоответствие calling convention (`__stdcall` vs `__cdecl`).
- Пропущен `extern "C"` при линковке C-функций из C++.

### LNK2001 — Unresolved External (Subsystem)

**Файл:** `errors/lnk2001-unresolved-external.md`

**Симптом:**
```
LNK2001: unresolved external symbol _main
LNK2001: unresolved external symbol _WinMain@16
```

**Причина:** несоответствие `/SUBSYSTEM` и entry point:
- `/SUBSYSTEM:CONSOLE` требует `main`.
- `/SUBSYSTEM:WINDOWS` требует `WinMain`.

**Решение:** проверить Linker → System → SubSystem.

### LNK1120 — Link Failed Summary

**Файл:** `errors/lnk1120-link-failed.md`

**Симптом:**
```
fatal error LNK1120: 1 unresolved externals
```

**Важно:** LNK1120 — это итоговая агрегированная ошибка. Она всегда сопровождается
LNK2019 или LNK2001, которые и нужно диагностировать.

---

## .vsconfig — установка компонентов VS

Файл `.vsconfig` содержит манифест компонентов Visual Studio, необходимых
для сборки native C++ проектов.

Компоненты, включённые в манифест:

| Компонент | Назначение |
|---|---|
| `Microsoft.VisualStudio.Workload.NativeDesktop` | Рабочая нагрузка Desktop C++ |
| `Microsoft.VisualStudio.Component.VC.Tools.x86.x64` | MSVC v143 — x64/x86 |
| `Microsoft.VisualStudio.Component.VC.Tools.ARM64` | MSVC v143 — ARM64 |
| `Microsoft.VisualStudio.Component.VC.v141.x86.x64` | MSVC v141 (VS 2017) — x64/x86 |
| `Microsoft.VisualStudio.Component.Windows10SDK.19041` | Windows 10 SDK 10.0.19041 |
| `Microsoft.VisualStudio.Component.Windows10SDK.18362` | Windows 10 SDK 10.0.18362 |
| `Microsoft.VisualStudio.Component.Windows11SDK.22621` | Windows 11 SDK |
| `Microsoft.VisualStudio.Component.VC.CMake.Project` | Поддержка CMake |
| `Microsoft.VisualStudio.Component.VC.ATL` | ATL библиотеки |
| `Microsoft.VisualStudio.Component.VC.MFC` | MFC библиотеки |
| `Microsoft.VisualStudio.Component.VC.Llvm.Clang` | Clang для Windows |
| `Microsoft.Component.MSBuild` | MSBuild |

**Импорт через VS Installer:**
1. Запустить **Visual Studio Installer**.
2. Нажать **Modify** на нужной установке.
3. Перейти на вкладку **Import**.
4. Выбрать `.vsconfig` из репозитория.
5. Нажать **Install**.

---

## Быстрый старт

### Ситуация: ошибка LNK1120 / LNK2019 при сборке

**Шаг 1 — диагностика окружения:**
```powershell
.\scripts\verify-environment.ps1
```
Если скрипт сообщает об отсутствии компонентов — установить их через `.vsconfig`.

**Шаг 2 — сравнить настройки:**
```powershell
.\scripts\diff-project-settings.ps1 -ProjectPath "ВашПроект.vcxproj"
```
Посмотреть, какие пути отличаются от эталонных.

**Шаг 3 — применить эталонные пути:**
```powershell
# Автоматически:
.\scripts\apply-default-paths.ps1 -Path "C:\SolutionDir" -Architecture x64

# Или вручную через Property Manager:
#   Добавить props/DefaultPaths.props к проекту
```

**Шаг 4 — пересобрать:**
```powershell
# Clean + Rebuild в Visual Studio
# Или через MSBuild:
msbuild ВашПроект.vcxproj /t:Rebuild /p:Configuration=Release
```

### Ситуация: новая установка VS

1. Импортировать `.vsconfig` в Visual Studio Installer.
2. Установить компоненты.
3. Подключить `DefaultPaths.props` к новому проекту.

---

## Типовой сценарий: kernel32.lib

### Проблема

После обновления Windows SDK или импорта чужих настроек проект перестал собираться:

```
LNK1120: 1 unresolved externals
LNK2019: unresolved external symbol CreateFileW referenced in function ...
```

### Диагностика

1. `verify-environment.ps1` — проверяет, что `kernel32.lib` существует.
2. Открыть свойства проекта → `VC++ Directories` → `Library Directories`.

**Неправильно (если пути сбиты):**
```
C:\CustomLibs;$(VC_LibraryPath_x64)
```

**Правильно (эталон):**
```
$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64
```

### Решение

**Вариант A (рекомендуемый) — через Property Manager:**
1. `View → Other Windows → Property Manager`
2. Правый клик на конфигурации → `Add Existing Property Sheet`
3. Выбрать `props/DefaultPaths.props`
4. Пересобрать

**Вариант B — через скрипт:**
```powershell
.\scripts\apply-default-paths.ps1 -Path "C:\MySolution"
```

**Вариант C — вручную:**
1. Правый клик на проекте → Properties
2. `VC++ Directories` → `Library Directories` → `<Edit...>`
3. Установить: `$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(NETFXKitsDir)Lib\um\x64`
4. OK → Rebuild

---

## Поддержка

Этот репозиторий предоставляет только конфигурационные файлы и документацию.
Он не содержит бинарных библиотек, установщиков или инструментов, не входящих
в состав Visual Studio и Windows SDK.

Для проблем, выходящих за рамки путей каталогов:
- [Официальная документация Visual Studio](https://docs.microsoft.com/en-us/visualstudio/)
- [Windows SDK documentation](https://docs.microsoft.com/en-us/windows/win32/)
- [Microsoft Q&A — Visual Studio](https://docs.microsoft.com/en-us/answers/topics/visual-studio.html)

---

## Лицензия

Документация предоставляется "как есть", без каких-либо гарантий.
Вы можете свободно использовать, копировать и изменять файлы этого репозитория.
