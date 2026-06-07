# LNK2019 — Unresolved External Symbol

## Симптом

```
error LNK2019: unresolved external symbol _WinMain@16 referenced in function "int __cdecl invoke_main(void)" (?invoke_main@@YAHXZ)
```

## Причины

1. **Отсутствует или неверный путь к kernel32.lib** — самая частая причина для `WinMain`, `CreateFile`, `CloseHandle` и других WinAPI функций.
2. **Пропущенная библиотека в Linker > Input > Additional Dependencies** — если проект использует специфические API (например, `ws2_32.lib` для сокетов).
3. **Несоответствие calling convention** — использование `__stdcall` там, где ожидается `__cdecl`, или наоборот.
4. **Пропущенный `extern "C"`** — в C++ коде при линковке C-библиотек.

## Решение

1. Восстановить Library Directories до эталонных значений (см. `vc++-directories.md`).
2. Добавить недостающие `.lib` в **Linker > Input > Additional Dependencies**.
3. Для C-функций обернуть объявления в `extern "C"`.
4. Проверить, что все .obj файлы от текущей сборки (clean + rebuild).
