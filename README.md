<h1 align="center">ameni monitor</h1>

<p align="center">
  Панель мониторинга системы в реальном времени<br>
  CPU / Память / Диски / Сеть
</p>

<p align="center">
  Linux · Windows · Python 3 · zero dependencies
</p>

---

## Установка

```bash
curl -s https://raw.githubusercontent.com/inzexg-coder/ameni-vs-kernel/main/install.sh | bash
ameni monitor
```

Или вручную:

```bash
git clone https://github.com/inzexg-coder/ameni-vs-kernel
cd ameni-vs-kernel
.ameni/bin/ameni monitor
```

Браузер открывается автоматически на `http://localhost:3000`. Данные обновляются каждые 2 секунды.

---

## Команды

```
ameni monitor                Запустить панель мониторинга
ameni monitor --no-browser   Запустить без браузера
ameni help                   Показать справку
```

---

## Панель

Четыре карточки с метриками на тёмно-фиолетовом фоне:

**Процессор**
- Загрузка в процентах с цветным индикатором (<60% зелёный, <85% жёлтый, >85% красный)
- Load average (1мин / 5мин / 15мин)
- Количество ядер и частота каждого ядра (MHz)
- Температура (°C)

**Память**
- Использование RAM с цветным индикатором
- Доступно / Всего (GB)
- Использование Swap с цветным индикатором

**Диски**
- Для каждого раздела: точка монтирования, индикатор заполнения, процент, использовано/всего

**Сеть**
- Для каждого интерфейса: имя, RX (приём) / TX (передача)

**История (премиум)**
- График загрузки CPU за последние 30 минут
- Отрисовка на Canvas с градиентной заливкой

---

## Поддержка платформ

| Платформа | CPU | Память | Диски | Сеть | Температура |
|-----------|-----|--------|-------|------|-------------|
| Linux | /proc/stat | /proc/meminfo | /proc/mounts + statvfs | /proc/net/dev | /sys/class/thermal |
| Windows | kernel32.GetSystemTimes | GlobalMemoryStatusEx | PowerShell Get-CimInstance | Get-NetAdapterStatistics | нет |
| macOS | не реализовано | не реализовано | не реализовано | не реализовано | не реализовано |

Все чтения системы обёрнуты в try/except. Если источник недоступен, поле возвращает ноль или пустой массив. Сервер никогда не падает при отсутствии данных.

---

## API

```
GET /api/monitor/all       CPU + RAM + Disk + Network одним запросом
GET /api/monitor/cpu       Только CPU
GET /api/monitor/memory    Только RAM + Swap
GET /api/monitor/disk      Только диски
GET /api/monitor/network   Только сеть
GET /api/monitor/history   История метрик (премиум)
GET /api/premium           Статус премиум
GET /api/system            Информация о системе
```

### Формат ответа

```json
{
  "cpu": {
    "usage": 34.2,
    "cores": 8,
    "freq": [806, 940, 614, 652],
    "load_avg": [1.2, 0.8, 0.5],
    "temp": 48.2
  },
  "memory": {
    "total_gb": 6.9,
    "avail_gb": 2.0,
    "used_pct": 71.0,
    "swap_total_gb": 4.0,
    "swap_used_pct": 79.8
  },
  "disk": [
    {"mount": "/", "total_gb": 222.9, "used_gb": 84.2, "used_pct": 37.8, "fstype": "erofs"}
  ],
  "network": [
    {"iface": "wlan0", "rx_bytes": 123456, "tx_bytes": 65432}
  ]
}
```

---

## Премиум

```bash
AMENI_PREMIUM=1 ameni monitor
touch ~/.ameni/premium.key && ameni monitor
```

- Буфер истории метрик (1800 точек = 30 минут)
- Эндпоинт `/api/monitor/history`
- График CPU на Canvas

---

## Структура репозитория

```
ameni-vs-kernel/
├── server/app.py          HTTP-сервер с HTML-страницей
├── .ameni/bin/ameni       CLI запускатор
├── install.sh             Установщик
├── demo.html              Автономная демка (без сервера)
├── AGENTS.md              Контекст для AI-агентов
├── SKILL.md               Инструкция для AI-агентов
├── agents/openai.yaml     Метаданные для GPT Store
└── README.md
```

---

## Технологии

- Python 3 — стандартная библиотека (http.server, ctypes, json)
- HTML / CSS / JS — single-page, автообновление, Canvas график
- JetBrains Mono
- Тёмно-фиолетовая тема (#08040e, #a855f7)
- Ноль внешних зависимостей

---

<p align="center">
  <a href="https://github.com/inzexg-coder/ameni-vs-kernel">github.com/inzexg-coder/ameni-vs-kernel</a>
</p>
