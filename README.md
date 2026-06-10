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

### Перед началом — разрешите запуск скриптов

PowerShell по умолчанию блокирует запуск неподписанных скриптов. Перед любыми
командами откройте **PowerShell** и выполните:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

> Эта команда действует только в текущем сеансе PowerShell. При каждом новом
> открытии PowerShell выполняйте её снова. Без неё PowerShell выдаст ошибку
> «не удается загрузить файл, так как выполнение сценариев отключено».

---

### Всегда используйте префикс `.\` в PowerShell

Все команды выполняются **только в PowerShell** (не в cmd.exe). В PowerShell для запуска локальных файлов нужен префикс `.\`:

| Правильно | Неправильно |
|-----------|-------------|
| `.\ameni\bin\ameni.ps1 diagnose` | `ameni.ps1 diagnose` |
| `.\ameni\bin\ameni.ps1 check .` | `ameni\bin\ameni.ps1` |

> Без префикса `.\` PowerShell выдаст ошибку «не удается распознать команду».

> **Важно:** Команды с префиксом `.\` работают только в PowerShell. Обычная командная строка (cmd.exe) их не выполнит.

---



### Что вы увидите при диагностике

После выполнения `.\ameni\bin\ameni.ps1 diagnose` вы получите в консоли отчёт.
Вот что означают его части:

```
=== Environment Diagnostics ===
OS: Microsoft Windows 10.0.19045 (x64)
```

В первой строке выводится версия вашей операционной системы.

#### Статусы `[OK]`, `[WARN]`, `[ERROR]`

| Метка | Цвет | Значение |
|-------|------|----------|
| `[OK]` | Зелёный | ✅ Компонент найден, всё в порядке. Можно ничего не делать |
| `[WARN]` | Жёлтый | ⚠️ Скрипт чего-то не нашёл, но это **не ошибка**. Многие предупреждения нормальны и не влияют на сборку |
| `[ERROR]` | Красный | ❌ Проблема, которую нужно исправить. Обычно означает, что компонент не установлен |

#### Раздел vswhere

```
[OK] vswhere.exe: C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
       Visual Studio Community 2022 [17.x]
```

Проверяется, установлена ли Visual Studio. Если `[OK]` — студия найдена. Если `[WARN]` — vswhere не обнаружен (значит, Visual Studio Installer не установлен или VS не установлена).

#### Раздел Windows SDK

```
[OK] Windows Kits: C:\Program Files (x86)\Windows Kits\10
       SDK 10.0.19041.0: kernel32.lib найден
```

Проверяются Windows SDK и наличие `kernel32.lib`. Если `[OK]` — системные библиотеки доступны. Если `[WARN]` — какой-то SDK не содержит `kernel32.lib` (возможно, не установлен нужный компонент).

#### Раздел MSVC (компилятор C++)

```
[OK] MSVC 14.35 (VS 2022 Community)
       vcruntime.lib найден
```

Проверяется компилятор Microsoft Visual C++. Если `[OK]` — компилятор и его библиотеки найдены.

#### Прочие сообщения

```
[WARN] pwsh не найден. Используется Windows PowerShell.
```

`pwsh` — это PowerShell Core (кроссплатформенная версия). Если его нет — это **нормально**, используется встроенный в Windows PowerShell 5.1. На работу скриптов это не влияет.

---
Ниже написано, что делать, если Visual Studio ругается на библиотеки. Ничего устанавливать не нужно — у вас уже есть Visual Studio. Просто выполняйте шаги по порядку.

### Шаг 1 — Скачать репозиторий через консоль

Откройте **PowerShell** (нажмите Пуск, напишите `PowerShell`, откройте).

**Способ A — через Git (рекомендуется):**

> Перед выполнением любых команд откройте **PowerShell** и выполните `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

```powershell
git clone https://github.com/inzexg-coder/ameni-vs-kernel.git
cd ameni-vs-kernel
```

*Если Git не установлен — скачайте и распакуйте ZIP через консоль:*

> Не забудьте сначала выполнить `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

```powershell
Invoke-WebRequest -Uri "https://github.com/inzexg-coder/ameni-vs-kernel/archive/refs/heads/main.zip" -OutFile "ameni-vs-kernel.zip"
Expand-Archive -Path "ameni-vs-kernel.zip" -DestinationPath "."
cd ameni-vs-kernel-main
```

Готово — вы в директории с проектом, все команды ниже работают.

### Шаг 2 — Проверить, чего не хватает

> **Важно:** Все команды выполняются в **PowerShell**. Если вы открыли обычную командную строку (cmd.exe) — закройте её и откройте PowerShell (Пуск → напишите `PowerShell` → Enter).
>
> Перед запуском не забудьте: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

Вставьте эту команду в PowerShell и нажмите Enter:

```powershell
.\.ameni\bin\ameni.ps1 diagnose
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
[WARN] pwsh не найден. Используется Windows PowerShell.
```

Подробное описание всех строк вывода — см. раздел [«Что вы увидите при диагностике»](#что-вы-увидите-при-диагностике).

Если написано `[ERROR] kernel32.lib ОТСУТСТВУЕТ` — переходите к Шагу 5. Если всё зелёное — переходите к Шагу 3.

### Шаг 3 — Сверить настройки проекта

Найдите ваш .vcxproj файл (он лежит в папке с вашим проектом, рядом с .sln). Запустите:

```powershell
.\.ameni\bin\ameni.ps1 check C:\Путь\к\вашему\проекту
```

Если после этой команды написано `[OK]  Все настройки совпадают с эталоном.` — всё в порядке, проблема не в путях.

Если написано `[!]  LibraryDirectories non-standard` — переходите к Шагу 4.

### Шаг 4 — Автоматически исправить .vcxproj (через CLI)

Эта команда сама пропишет правильные пути прямо в ваш файл проекта. Она сделает резервную копию (`.bak`), так что ничего не сломается.

```powershell
.\.ameni\bin\ameni.ps1 fix C:\Путь\к\вашему\проекту x64
```

Параметр `x64` — это архитектура. Если ваш проект 32-битный — укажите `x86`, если ARM64 — `ARM64`.

После этой команды пути библиотек будут приведены к эталону. Попробуйте собрать проект заново.

Если хотите откатить изменения — переименуйте .bak обратно:
```powershell
Rename-Item "МойПроект.vcxproj.bak" "МойПроект.vcxproj"
```

Если ошибка осталась — переходите к Шагу 5.

### Шаг 5 — Установить недостающие компоненты Visual Studio (через CLI)

Если `fix` не помог — возможно, не установлены нужные компоненты Visual Studio. Импортируйте `.vsconfig` через VS Installer CLI:

```powershell
.\.ameni\bin\ameni.ps1 vsconfig
```

Эта команда найдёт вашу установку Visual Studio через vswhere и запустит установщик с конфигурацией из `.vsconfig`. Никаких кнопок — всё через консоль.

После установки перезапустите Visual Studio и повторите Шаг 2.


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
.\.ameni\bin\ameni.ps1 diagnose
.\.ameni\bin\ameni.ps1 check C:\MyProject
.\.ameni\bin\ameni.ps1 props
.\.ameni\bin\ameni.ps1 errors lnk1104-cannot-open-file
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

---

## Связанные скиллы

<p align="center">
  <a href="https://github.com/inzexg-coder/ameni-tg-parser">
    <img src=".ameni/assets/skill-tg.svg" width="64" alt="TG Parser">
  </a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://github.com/inzexg-coder/ameni-vs-kernel">
    <img src=".ameni/assets/skill-vs.svg" width="64" alt="VS Kernel">
  </a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://github.com/inzexg-coder/fide-rating-calc">
    <img src=".ameni/assets/skill-fide.svg" width="64" alt="FIDE Calc">
  </a>
</p>

<p align="center">

| Скилл | Описание |
|-------|----------|
| [**ameni-tg-parser**](https://github.com/inzexg-coder/ameni-tg-parser) | Telegram Message Parser — анализ и визуализация чатов |
| [**ameni-vs-kernel**](https://github.com/inzexg-coder/ameni-vs-kernel) | VS Kernel — диагностика Visual Studio, LNK-ошибки, .vcxproj |
| [**fide-rating-calc**](https://github.com/inzexg-coder/fide-rating-calc) | FIDE Rating Calculator — оценка FIDE-рейтинга по партиям |

</p>

