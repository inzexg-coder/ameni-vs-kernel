---
name: ameni-monitor
description: "Real-time Linux system monitoring dashboard — CPU, RAM, disks, network. Use when the task involves checking system health, monitoring resource usage, diagnosing performance issues, or tracking system metrics over time."
---

# Ameni Monitor — System Dashboard

Веб-дашборд для мониторинга системы в реальном времени.

## Запуск

```bash
.ameni/bin/ameni monitor
```

Открывает http://localhost:3000 с дашбордом, обновление каждые 2 секунды.

## Бесплатные функции

- CPU: загрузка, частота ядер, load average, температура
- Memory: RAM used/available, swap
- Disks: список разделов с цветовой индикацией
- Network: интерфейсы, RX/TX

## Премиум

`AMENI_PREMIUM=1` — история метрик за 30 минут.

## API для AI-агентов

```python
import requests
r = requests.get("http://localhost:3000/api/monitor/all")
print(r.json())  # CPU, RAM, Disk, Network
```
