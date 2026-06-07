# LNK1104 — Cannot Open File

## Симптом

```
fatal error LNK1104: cannot open file 'kernel32.lib'
```

## Причины

1. **Файл kernel32.lib отсутствует** — Windows SDK не установлен или повреждён.
2. **Путь к библиотекам содержит неверную директорию** — Library Directories указывает на
   несуществующий путь.
3. **Файл заблокирован антивирусом** или другим процессом.
4. **Разрядность не совпадает** — проект x86, а Library Directories указывает на x64 (или наоборот).

## Решение

1. Запустить `verify-environment.ps1` для диагностики.
2. Восстановить Library Directories (см. `vc++-directories.md`).
3. Если файла физически нет — переустановить Windows SDK через Visual Studio Installer:
   - Открыть Visual Studio Installer
   - Modify → Individual Components → найти "Windows 10 SDK" или "Windows 11 SDK"
   - Установить недостающие компоненты
4. Для x86 проектов: использовать `$(VC_LibraryPath_x86);$(WindowsSDK_LibraryPath_x86);$(NETFXKitsDir)Lib\um\x86`
