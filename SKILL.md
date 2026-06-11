---
name: ameni-vs-kernel
description: "Visual Studio C++ build diagnostics and repair toolkit. Use when the task involves troubleshooting LNK errors (LNK2019, LNK1104, LNK1120), restoring VC++ library paths, fixing kernel32.lib resolution failures, diagnosing Visual Studio installation issues, comparing .vcxproj settings against reference configurations, applying corrected library directory paths, importing .vsconfig manifests via VS Installer CLI, or working with MSBuild props files for C++ projects targeting x86/x64/ARM64."
---

# Ameni VS Kernel — Visual Studio C++ Configuration Archive

Диагностика и исправление ошибок сборки Visual Studio C++ (LNK2019, LNK1104, LNK1120) путём восстановления путей библиотек и компонентов.

## Структура

```
ameni-vs-kernel/
├── props/                    # Эталонные .props конфигурации
│   ├── DefaultPaths.props          # Базовые пути
│   ├── DefaultPaths-x86.props      # x86 специфика
│   ├── DefaultPaths-ARM64.props    # ARM64 специфика
│   ├── DebugSettings.props         # Настройки отладки
│   ├── AdvancedSettings.props      # Продвинутые настройки
│   ├── DLL.props                   # DLL-проекты
│   ├── StaticLib.props             # Статические библиотеки
│   └── Driver.props                # Драйверы
├── errors/                   # Справочник ошибок
│   ├── lnk1104-cannot-open-file.md
│   ├── lnk1120-link-failed.md
│   ├── lnk2001-unresolved-external.md
│   └── lnk2019-unresolved-external.md
├── scripts/                  # PowerShell скрипты
│   ├── verify-environment.ps1     # Диагностика окружения
│   ├── apply-default-paths.ps1    # Применение путей
│   └── diff-project-settings.ps1  # Сравнение .vcxproj
├── vs2022/                   # Конфиги для VS 2022
├── vs2025/                   # Конфиги для VS 2025
├── vs2017/                   # Конфиги для VS 2017
├── .vsconfig                 # Манифест компонентов VS
├── .ameni/                   # CLI агент
│   ├── bin/ameni.ps1        # PowerShell CLI
│   └── bin/ameni             # Bash-диспетчер (Linux)
├── general.md                # Общие настройки
├── advanced.md               # Продвинутые свойства
├── debugging.md              # Настройки отладчика
└── vc++-directories.md       # Пути VC++ каталогов
```

## Workflows

### Диагностика (Windows)

```powershell
# 1. Разрешить скрипты
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Запуск диагностики окружения
.\\.ameni\\bin\\ameni.ps1 diagnose

# 3. Сверить настройки проекта
.\\.ameni\\bin\\ameni.ps1 check C:\\path\\to\\project

# 4. Автоматически исправить .vcxproj
.\\.ameni\\bin\\ameni.ps1 fix C:\\path\\to\\project x64

# 5. Установить недостающие компоненты VS
.\\.ameni\\bin\\ameni.ps1 vsconfig
```

### Arch Linux (референс)

```bash
export PATH="$PATH:$(pwd)/.ameni/bin"
ameni diagnose    # Диагностика через mono/PowerShell
```

## Справочник ошибок

В папке `errors/` — файлы с диагностикой каждой LNK-ошибки:
- **LNK1104** — cannot open file (обычно отсутствует библиотека)
- **LNK1120** — unresolved externals (счётчик)
- **LNK2001** — unresolved external symbol (внешняя)
- **LNK2019** — unresolved external symbol (функция)

Каждый файл содержит: причины, пошаговое решение, пример кода с ошибкой.

## Решения проблем

| Симптом | Действие |
|---|---|
| `[ERROR] kernel32.lib ОТСУТСТВУЕТ` | Шаг 5 — установка компонентов VS |
| `[!] LibraryDirectories non-standard` | Шаг 4 — fix через CLI |
| `[OK]` всё зелёное, но сборка падает | Проверить код, `Additional Dependencies`, `SUBSYSTEM` |
| Ошибка на Linux | Использовать как документацию, CLI через mono |

## When to Use

- При любой LNK-ошибке в Visual Studio C++
- Когда Visual Studio не находит `kernel32.lib` или другие системные библиотеки
- Для сверки настроек проекта с эталонными конфигурациями
- При настройке CI/CD для C++ проектов под Windows

## References

Все ключевые файлы (`props/`, `errors/`, `vs2022/vc++-directories.md`) содержат подробные комментарии. Загружайте соответствующий файл в контекст при работе с конкретной ошибкой или компонентом.
