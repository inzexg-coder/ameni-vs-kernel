# LNK2001 — Unresolved External Symbol (неразрешенный внешний символ)

## Отличие от LNK2019

LNK2001 обычно означает, что символ объявлен, но нигде не определён, в отличие от LNK2019,
который означает, что определение не найдено в принципе.

## Типичные сценарии

| Ошибка | Причина |
|---|---|
| `LNK2001: unresolved external symbol __imp__MessageBoxW@16` | Отсутствует `User32.lib` |
| `LNK2001: unresolved external symbol _main` | Тип проекта — Console (/SUBSYSTEM:CONSOLE), но нет функции `main` |
| `LNK2001: unresolved external symbol _WinMain@16` | Тип проекта — Windows (/SUBSYSTEM:WINDOWS), но нет `WinMain` |
| `LNK2001: unresolved external symbol __iob_func` | MSVC версия не совпадает с ожидаемой стандартной библиотекой |

## Решение

1. Проверить `/SUBSYSTEM` в **Linker > System** — должно соответствовать типу приложения.
2. Добавить нужные `.lib` в **Linker > Input > Additional Dependencies**.
3. Для `__iob_func`: обновить проект до актуального toolset'а или добавить заглушку.
4. Выполнить clean + rebuild.
