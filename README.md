<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="130">
<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-38bdf8?labelColor=222" alt="Version 0.2.0">
</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Ameni_Monitor-System_Dashboard-%23a855f7?labelColor=222" alt="Ameni Monitor">
  <img src="https://img.shields.io/badge/platform-linux+windows-%234CAF50?labelColor=222" alt="Linux+Windows">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?labelColor=222" alt="MIT">
  <img src="https://img.shields.io/badge/dependencies-cryptography-7c3aed?labelColor=222" alt="cryptography">
</p>

<h1 align="center">Ameni Monitor — панель мониторинга</h1>

<p align="center">
  Мониторинг системы в реальном времени в браузере.<br>
  CPU / Память / Диски / Сеть / Зарядка. Linux и Windows.
</p>

<p align="center">
  <a href="#установка">Установка</a> &middot;
  <a href="#использование">Использование</a> &middot;
  <a href="#дашборд">Дашборд</a> &middot;
  <a href="#статусы">Статусы</a> &middot;
  <a href="#premium">Premium</a> &middot;
  <a href="#api">API</a>
</p>

<br>

## Установка

```bash
curl -s https://raw.githubusercontent.com/inzexg-coder/ameni-vs-kernel/main/install.sh | bash
ameni
```

### Вручную

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel
cd ameni-vs-kernel
chmod +x .ameni/bin/ameni
.ameni/bin/ameni
```

Браузер открывается автоматически. Дашборд обновляется каждые 2 секунды.

<br>

## Использование

| Команда | Описание |
|---------|----------|
| `ameni` | Запустить панель мониторинга |
| `ameni --no-browser` | Запустить без открытия браузера |
| `ameni help` | Показать справку |

### Поддержка платформ

| Платформа | CPU | Память | Диски | Сеть | Батарея |
|-----------|-----|--------|-------|------|---------|
| Linux | /proc/stat | /proc/meminfo | /proc/mounts | /proc/net/dev | /sys/class/power_supply |
| Windows | kernel32 | GlobalMemoryStatusEx | Get-CimInstance | Get-NetAdapterStatistics | WMI |

<br>

## Дашборд

Веб-интерфейс на светлом фоне с сиреневыми акцентами. Все метрики распределены по карточкам-нодам, соединённым фоновыми линиями.

### Основные блоки

| Блок | Метрики |
|------|---------|
| **CPU** | Загрузка с цветным индикатором, Load Average, Cores, частота, температура |
| **Memory** | RAM с цветным индикатором, Avail, Swap |
| **Uptime** | Время работы системы |
| **Battery** | Процент заряда, статус (зарядка/разрядка) |
| **Disk** | Список разделов с заполнением |
| **Network** | Интерфейсы с RX/TX |
| **Processes** | Топ процессов по памяти |

### Premium

| Блок | Описание |
|------|----------|
| **History** | График загрузки CPU за последние 6 минут |
| **Disk I/O** | Чтение/запись по дискам |

Для активации premium нужна подписка на amenoke.ru или офлайн-ключ.

### Анимации

Каждый блок имеет ассоциативную CSS-анимацию:

- **CPU** — пульсирующее свечение рамки
- **Memory** — перелив на прогресс-барах
- **Uptime** — бегущая боковая полоса
- **Battery** — иконка молнии при зарядке
- **Disk** — сканирующая линия
- **Network** — волновой индикатор
- **Processes** — мигающий курсор
- **History** — пульсирующая подсветка низа

<br>

## Статусы

### Цвета значений и прогресс-баров

| Диапазон | Цвет |
|----------|------|
| < 50% | Зелёный |
| 50-69% | Жёлтый |
| 70-84% | Оранжевый |
| >= 85% | Красный |

<br>

## Premium

Две версии проверки:

**Online** — авторизация через amenoke.ru. Пользователь вводит логин/пароль, сервер проверяет статус подписки через API amenoke.ru.

**Offline** — лицензионный ключ с Ed25519-подписью. Ключ проверяется локально, без доступа к сети.

### Формат офлайн-ключа

```
base64(payload).base64(signature)
```

payload содержит email, дату истечения, machine_id. Подпись верифицируется открытым ключом Ed25519.

### Генерация ключа

```bash
python3 server/keygen.py
```

Создаёт лицензию в `~/.ameni/license.key` (если есть приватный ключ).

<br>

## API

```
GET  /api/monitor/all       Все метрики
GET  /api/monitor/cpu       CPU
GET  /api/monitor/memory    RAM + Swap
GET  /api/monitor/disk      Диски
GET  /api/monitor/network   Сеть
GET  /api/system            Информация о системе
GET  /api/premium           Статус премиума
POST /api/login             Авторизация на amenoke.ru
POST /api/logout            Выход
POST /api/activate          Активация офлайн-ключа
```

### Формат ответа

```json
{
  "cpu": {"usage": 34.2, "cores": 8, "freq": [806, 940], "load_avg": [1.2, 0.8, 0.5], "temp": 48.2},
  "memory": {"total_gb": 6.9, "avail_gb": 2.0, "used_pct": 71.0, "swap_total_gb": 4.0, "swap_used_pct": 79.8},
  "disk": [{"mount": "/", "total_gb": 222.9, "used_gb": 84.2, "used_pct": 37.8}],
  "network": [{"iface": "wlan0", "rx_bytes": 123456, "tx_bytes": 65432}],
  "uptime": {"days": 1, "hours": 5, "mins": 23},
  "battery": {"pct": 67, "status": "Charging"},
  "processes": [{"pid": 1234, "name": "firefox", "mem": 890}],
  "diskio": {"sda": {"rbytes": 123456, "wbytes": 789012}}
}
```

<br>

## Структура проекта

```
ameni-vs-kernel/
  server/
    app.py          HTTP-сервер и API
    dashboard.html  Веб-интерфейс мониторинга
    keygen.py       Генератор лицензионных ключей
  .ameni/
    bin/ameni       Запуск (shell-скрипт)
    assets/         Логотип
  install.sh        Скрипт установки
  README.md         Этот файл
  SKILL.md          Инструкция для Codex CLI
  AGENTS.md         Инструкция для агента
```

<br>

---

<p align="center">
  <a href="https://github.com/inzexg-coder/ameni-vs-kernel">github.com/inzexg-coder/ameni-vs-kernel</a>
</p>
