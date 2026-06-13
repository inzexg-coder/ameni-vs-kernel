# AGENTS.md — ameni monitor

Real-time Linux system monitoring dashboard (CPU, RAM, disks, network).

## Структура

```
ameni-monitor/
├── server/app.py          # HTTP-сервер с HTML-страницей
├── .ameni/bin/ameni       # CLI (ameni monitor)
├── index.html             # Статическая версия
├── install.sh             # Установщик
├── AGENTS.md / SKILL.md   # Контекст для AI
└── README.md
```

## Запуск

```bash
cd /root/ameni-vs-kernel
.ameni/bin/ameni monitor
```

## API

| GET | Описание |
|-----|----------|
| `/api/monitor/all` | CPU + RAM + Disk + Network |
| `/api/monitor/history` | История (premium) |
| `/api/premium` | Статус premium |
| `/api/system` | Информация об ОС |

## Конвенции

- Python 3, чистый stdlib
- Без комментариев в коде
- Сиреневая тема (#08040e)
- Без эмодзи
