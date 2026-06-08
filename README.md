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
  Гайд по исправлению LNK2019, LNK1104, LNK1120<br>
  и восстановлению путей библиотек в Visual Studio C++
</p>

<p align="center">
  <a href="#как-это-работает">Как это работает</a> &middot;
  <a href="#windows">Windows</a> &middot;
  <a href="#arch-linux">Arch Linux</a> &middot;
  <a href="#cli-агент">CLI агент</a> &middot;
  <a href="#полный-справочник">Полный справочник</a>
</p>

---

## Как это работает

Когда Visual Studio выдаёт ошибку вроде `LNK1104: cannot open file 'kernel32.lib'` или `LNK2019: unresolved external symbol`, это почти всегда означает, что Visual Studio не может найти системные библиотеки. Пути к ним либо сбились, либо компонент не установлен.

В репозитории лежат эталонные настройки путей и скрипты, которые возвращают всё как было.

---

## Windows

Ниже написано, что делать, если Visual Studio ругается на библиотеки. Ничего устанавливать не нужно — у вас уже есть Visual Studio. Просто выполняйте шаги по порядку.

### Шаг 1 — Скачать и открыть

Нажмите зелёную кнопку **Code** на этой странице, выберите **Download ZIP**. Распакуйте папку куда-нибудь на рабочий стол.

Откройте **PowerShell** (нажмите Пуск, напишите `PowerShell`, откройте). Перейдите в распакованную папку:

```powershell
cd C:\Users\ВашеИмя\Desktop\ameni-vs-kernel
```

Готово.

### Шаг 2 — Проверить, чего не хватает

Вставьте эту команду в PowerShell и нажмите Enter:

```powershell
.\ameni\bin\ameni.ps1 diagnose
```

Вы увидите примерно такое:

```
=== Environment Diagnostics ===
[OK] vswhere.exe найден
     Установка: Visual Studio Community 2022 [17.x]
[OK] Windows Kits найден
     SDK 10.0.19041.0: kernel32.lib найден
[OK] MSVC 14.35 (VS 2022 Community)
     vcruntime.lib найден
```

Зелёные `[OK]` — всё хорошо. Красные `[ERROR]` — чего-то не хватает.

Если написано `[ERROR] kernel32.lib ОТСУТСТВУЕТ` — переходите к Шагу 5. Если всё зелёное — переходите к Шагу 3.

### Шаг 3 — Сверить настройки проекта

Найдите ваш .vcxproj файл (он лежит в папке с вашим проектом, рядом с .sln). Запустите:

```powershell
.\ameni\bin\ameni.ps1 check C:\Путь\к\вашему\проекту
```

Если после этой команды написано `[INFO]  Check complete.` и нет красных строк — всё в порядке, проблема не в путях.

Если написано `LibraryDirectories non-standard` или что-то подобное — переходите к Шагу 4.

### Шаг 4 — Подключить правильные пути через Property Sheet (самый лёгкий способ)

Откройте ваш проект в Visual Studio. В меню сверху найдите **View -> Property Manager** (если не видите, нажмите Ctrl+Q и напишите Property Manager).

Справа появится окошко. Раскройте там свою конфигурацию (например, Debug | x64). Нажмите на ней **правой кнопкой** мыши, выберите **Add Existing Property Sheet...**.

Найдите в распакованной папке `props/DefaultPaths.props` и нажмите **Open**.

```
Где лежит: C:\Users\ВашеИмя\Desktop\ameni-vs-kernel\props\DefaultPaths.props
```

Всё. Пути исправлены. Попробуйте собрать проект заново.

Если ошибка осталась — переходите к Шагу 5.

### Шаг 5 — Автоматически исправить .vcxproj (продвинутый способ)

Эта команда сама пропишет правильные пути прямо в ваш файл проекта. Она сделает резервную копию, так что ничего не сломается.

```powershell
.\ameni\bin\ameni.ps1 check C:\Путь\к\папке\с\проектом
pwsh .\scripts\apply-default-paths.ps1 -Path "C:\Путь\к\вашему\проекту" -Architecture x64
```

Параметр `-Architecture` — это x64, если ваш компьютер 64-битный (у большинства так). Если не уверены — оставьте x64.

После этой команды попробуйте собрать проект.

Если хотите откатить — переименуйте файлы .bak обратно:
```powershell
Rename-Item "МойПроект.vcxproj.bak" "МойПроект.vcxproj"
```

### Шаг 6 — Переустановить компоненты Visual Studio

Если ничего не помогло, возможно, какой-то компонент Visual Studio не установлен. 

Откройте **Visual Studio Installer** (найдите через Пуск). Нажмите **Изменить** рядом с вашей версией Visual Studio. Перейдите на вкладку **Импорт конфигурации**. Выберите файл `.vsconfig`, который лежит в распакованной папке. Нажмите **Импорт**, потом **Установить**.

После установки повторите Шаг 1.

### Если всё ещё не работает

Проблема не в путях. Проверьте код: возможно, вы забыли подключить какую-то библиотеку в свойствах проекта (Additional Dependencies) или неправильно указали точку входа (SUBSYSTEM). Почитайте про вашу ошибку в папке `errors/`.

<br>

---

## Arch Linux

Репозиторий содержит эталонную конфигурацию VC++ Directories, скрипты диагностики PowerShell и манифест .vsconfig для Visual Studio. Нативный use-case — восстановление сборки C++ под Windows. На Arch Linux используется как референсная документация для чтения, а CLI-агент выполняет диагностику окружения.

### Установка

```bash
sudo pacman -S dotnet-sdk powershell mono
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
export PATH="$PATH:$(pwd)/.ameni/bin"
```

PKGBUILD прилагается:

```bash
makepkg -si      # собирает пакет, устанавливает ameni в /usr/bin
```

### CLI — диагностика окружения

```bash
ameni vs diagnose
```

Вывод содержит состояние toolchain: dotnet SDK, Mono JIT, PowerShell Core, GCC/G++/Clang, make/cmake. Скрипт детектит среду без side-эффектов.

Для запуска PowerShell-скриптов (verify-environment.ps1) на Arch:

```bash
sudo pacman -S powershell
pwsh ./scripts/verify-environment.ps1
```

Скрипт ожидает Windows SDK и VS, на Linux упадёт на проверках vswhere и Windows Kits — штатное поведение.

### CLI — валидация .vcxproj

```bash
ameni vs check ./path/to/project
```

Читает LibraryDirectories в .vcxproj, сравнивает с эталонным паттерном `$(VC_LibraryPath_x64)`. Несоответствие говорит о том, что файл был модифицирован вручную или через некорректный импорт. Полезно при код-ревью кросс-платформенных репозиториев, где .vcxproj может быть испорчен merge conflict-ом.

### Что лежит в репозитории

| Компонент | Назначение |
|-----------|------------|
| `props/*.props` | Property Sheets для VS Property Manager. Безопасное переопределение путей без редактирования .vcxproj |
| `scripts/verify-environment.ps1` | Проверка установки VS, MSVC, Windows SDK через vswhere |
| `scripts/diff-project-settings.ps1` | Дифф .vcxproj против эталонных VC++ Directories |
| `scripts/apply-default-paths.ps1` | Автоматическая запись эталонных путей в .vcxproj (Backup = .bak) |
| `errors/*.md` | Референс LNK1104, LNK2019, LNK2001, LNK1120 |
| `vs2017/`, `vs2022/`, `vs2025/` | Обвязка general.md + vc++-directories.md под конкретный Platform Toolset |
| `.vsconfig` | Манифест компонентов для VS Installer. Импортируется через Installer -> Import |

### Типовой сценарий использования на Arch

1. `ameni vs diagnose` — убедиться, что dotnet/Mono/pwsh в наличии
2. `ameni vs check ./repo/src` — проверить .vcxproj на битые пути
3. Открыть `errors/lnk2019-unresolved-external.md` — понять матчасть
4. Если нужно применить изменения на Windows-машине — скопировать `scripts/` и `.vsconfig`

<br>

---

## CLI агент

Доступен на обеих платформах. Windows использует `ameni.ps1`, Arch Linux — `ameni` (bash).

### Команды

```
ameni vs diagnose          — диагностика VS toolchain (Windows) / окружения (Linux)
ameni vs check [path]      — проверка .vcxproj на нестандартные пути
ameni vs props             — список всех property sheets
ameni vs errors [name]     — справка по ошибке (lnk1104, lnk2019 и т.д.)
ameni vs about             — информация об агенте
ameni vs help              — полный мануал
```

### Windows (PowerShell)

```powershell
.\ameni\bin\ameni.ps1 diagnose
.\ameni\bin\ameni.ps1 check C:\MyProject
.\ameni\bin\ameni.ps1 props
.\ameni\bin\ameni.ps1 errors lnk1104-cannot-open-file
```

### Arch Linux (bash)

```bash
ameni vs diagnose
ameni vs check ./MyProject
ameni vs props
ameni vs errors lnk1104-cannot-open-file
```

<br>

---

## Полный справочник

### Property Sheets (props/)

| Файл | Когда использовать |
|------|-------------------|
| `DefaultPaths.props` | Всегда для x64 проектов. Исправляет VC++ Directories |
| `DefaultPaths-x86.props` | Для 32-битных проектов |
| `DefaultPaths-ARM64.props` | Для ARM64 |
| `AdvancedSettings.props` | Дополнительные опции C/C++ |
| `DLL.props` | Проекты, собираемые как DLL |
| `StaticLib.props` | Статические библиотеки (.lib) |
| `DebugSettings.props` | Отладочные символы, PDB |
| `Driver.props` | WDK-специфичные настройки |

### Ошибки линковки (errors/)

| Файл | Ошибка | Типичная причина |
|------|--------|-----------------|
| `lnk1104-cannot-open-file.md` | LNK1104 | SDK не установлен, пути сбиты |
| `lnk2019-unresolved-external.md` | LNK2019 | Неправильные Library Directories |
| `lnk2001-unresolved-external.md` | LNK2001 | Неверный /SUBSYSTEM |
| `lnk1120-link-failed.md` | LNK1120 | Следствие одной из ошибок выше |

### Конфиги по версиям VS

| Папка | Toolset | MSVC |
|-------|---------|------|
| `vs2017/` | v141 | 14.1x |
| `vs2022/` | v143 | 14.3x |
| `vs2025/` | v144 | 14.4x |

### Скрипты (scripts/)

```
scripts/
  verify-environment.ps1       — проверка VS, SDK, MSVC
  diff-project-settings.ps1    — дифф .vcxproj с эталоном
  apply-default-paths.ps1      — автоисправление .vcxproj
```

### Архитектура репозитория

```
.ameni/
  assets/          — логотип
  bin/
    ameni          — CLI (bash, Arch Linux / Git Bash / WSL)
    ameni.ps1      — CLI (PowerShell, Windows)
props/             — Property Sheets
scripts/           — PowerShell скрипты
errors/            — документация по ошибкам
vs2017-2025/       — конфиги по версиям
PKGBUILD           — Arch Linux
.vsconfig          — манифест VS Installer
```

---

<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="32">
  <br>
  <a href="https://github.com/inzexg-coder">@inzexg-coder</a>
</p>
