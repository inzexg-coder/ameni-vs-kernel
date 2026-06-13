<p align="center">
  <img src=".ameni/assets/ameni-logo.svg" width="80" height="80" alt="ameni logo">
</p>

<h1 align="center">ameni monitor</h1>

<p align="center">
  Панель мониторинга системы в браузере<br>
  CPU / Память / Диски / Сеть
</p>

<p align="center">
  <sub>Python 3 · zero dependencies · Linux / Windows</sub>
</p>

---

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

Браузер открывается автоматически на http://localhost:3000. Данные обновляются каждые 2 секунды.

---

## Использование

```
ameni                        Запустить панель мониторинга
ameni --no-browser           Запустить без открытия браузера
ameni help                   Показать справку
```

---

## Дашборд

Четыре карточки с метриками на тёмно-фиолетовом фоне:

**CPU**
- Загрузка с цветным индикатором (<60% зелёный, <85% жёлтый, >85% красный)
- Load average (1 / 5 / 15 мин)
- Количество ядер и частота каждого (MHz)
- Температура (°C)

**Память**
- Использование RAM с цветным индикатором
- Доступно / Всего
- Swap

**Диски**
- Список разделов с индикатором заполнения

**Сеть**
- Активные интерфейсы, RX/TX

**История (премиум)**
- График CPU за последние 30 минут
- Canvas с градиентом

---

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

---

## Премиум

```bash
AMENI_PREMIUM=1 ameni
touch ~/.ameni/premium.key && ameni
```

- Буфер истории на 30 минут
- График CPU на дашборде

---

<p align="center">
  <a href="https://github.com/inzexg-coder/ameni-vs-kernel">github.com/inzexg-coder/ameni-vs-kernel</a>
</p>
