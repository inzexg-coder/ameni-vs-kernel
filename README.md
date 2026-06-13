<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" alt="Ameni" width="130">
<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-38bdf8?labelColor=222" alt="Version 0.1.0">
</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Ameni_Monitor-System_Dashboard-%23a855f7?labelColor=222" alt="Ameni Monitor">
  <img src="https://img.shields.io/badge/platform-linux+windows-%234CAF50?labelColor=222" alt="Linux+Windows">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?labelColor=222" alt="MIT">
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?labelColor=222" alt="Zero dependencies">
</p>

<h1 align="center">Ameni Monitor — панель мониторинга</h1>

<p align="center">
  Мониторинг системы в реальном времени в браузере.<br>
  CPU / Память / Диски / Сеть. Linux и Windows.
</p>

<p align="center">
  <a href="#установка">Установка</a> &middot;
  <a href="#использование">Использование</a> &middot;
  <a href="#дашборд">Дашборд</a> &middot;
  <a href="#api">API</a> &middot;
  <a href="#премиум">Премиум</a>
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
| `ameni --no-browser` | Запустить без браузера |
| `ameni help` | Показать справку |

### Поддержка платформ

| Платформа | CPU | Память | Диски | Сеть |
|-----------|-----|--------|-------|------|
| Linux | /proc/stat | /proc/meminfo | /proc/mounts | /proc/net/dev |
| Windows | kernel32 | GlobalMemoryStatusEx | Get-CimInstance | Get-NetAdapterStatistics |

<br>

## Дашборд

Четыре карточки с метриками на тёмно-фиолетовом фоне:

**CPU** — загрузка с цветным индикатором, load average, частота ядер, температура

**Память** — RAM и Swap с цветными индикаторами

**Диски** — список разделов с заполнением

**Сеть** — интерфейсы с RX/TX

### Статусы индикаторов

| Заполнение | Цвет |
|------------|------|
| < 60% | Зелёный |
| 60-85% | Жёлтый |
| > 85% | Красный |

<br>

## API

```
GET /api/monitor/all       Все метрики
GET /api/monitor/cpu       CPU
GET /api/monitor/memory    RAM + Swap
GET /api/monitor/disk      Диски
GET /api/monitor/network   Сеть
GET /api/monitor/history   История (премиум)
GET /api/premium           Статус премиум
GET /api/system            Информация о системе
```

### Формат ответа

```json
{
  "cpu": {"usage": 34.2, "cores": 8, "freq": [806, 940], "load_avg": [1.2, 0.8, 0.5], "temp": 48.2},
  "memory": {"total_gb": 6.9, "avail_gb": 2.0, "used_pct": 71.0, "swap_total_gb": 4.0, "swap_used_pct": 79.8},
  "disk": [{"mount": "/", "total_gb": 222.9, "used_gb": 84.2, "used_pct": 37.8}],
  "network": [{"iface": "wlan0", "rx_bytes": 123456, "tx_bytes": 65432}]
}
```

<br>

## Премиум

```bash
AMENI_PREMIUM=1 ameni
touch ~/.ameni/premium.key && ameni
```

- Буфер истории на 30 минут
- График CPU на Canvas

---

<p align="center">
  <a href="https://github.com/inzexg-coder/ameni-vs-kernel">github.com/inzexg-coder/ameni-vs-kernel</a>
</p>
