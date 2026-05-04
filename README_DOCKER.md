# 🐳 Docker для Food Cost Calculator API

## Быстрый старт

### Запуск всех сервисов

```bash
docker-compose up -d
```

Это запустит:
- **PostgreSQL** (порт 5432)
- **Redis** (порт 6379)
- **FastAPI API** (порт 8000)

### Проверка логов

```bash
# Все логи
docker-compose logs -f

# Только API
docker-compose logs -f api

# Только БД
docker-compose logs -f db

# Только Redis
docker-compose logs -f redis
```

### Остановка

```bash
docker-compose down
```

С удалением томов (БД и Redis данные):
```bash
docker-compose down -v
```

---

## Доступ к сервисам

| Сервис | URL | Credentials |
|--------|-----|-------------|
| API Docs | http://localhost:8000/api/docs | - |
| PostgreSQL | localhost:5432 | `foodcost` / `foodcost_secret` |
| Redis | localhost:6379 | без пароля |

---

## Переменные окружения

### Для разработки (env.local)

Создайте файл `.env.local` в корне проекта:

```env
# База данных (для локальной разработки без Docker)
DB_URL=postgresql+asyncpg://foodcost:foodcost_secret@localhost:5432/foodcost_db

# Redis (для локальной разработки без Docker)
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=your_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Для Docker (env.docker)

Файл `env.docker` уже создан и используется автоматически при запуске через Docker.

---

## Разработка с горячей перезагрузкой

При запуске через `docker-compose up`, код монтируется в контейнер:

```yaml
volumes:
  - ./app:/app/app
```

Изменения в коде автоматически применяются благодаря флагу `--reload` в uvicorn.

---

## Миграции базы данных

### Создание миграций (Alembic)

```bash
# Внутри контейнера
docker-compose exec api bash

# Установка alembic (если еще не установлен)
pip install alembic

# Инициализация (один раз)
alembic init alembic

# Настройка alembic.ini и env.py
# ... (см. документацию Alembic)

# Автогенерация миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

### Применение миграций при старте

Добавьте в `docker-compose.yml`:

```yaml
command: >
  sh -c "alembic upgrade head && 
         uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

---

## Production сборка

### Оптимизированный Dockerfile для production

Для production уберите volume mounts и flag `--reload`:

```yaml
# docker-compose.prod.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      ENV: production
      DEBUG: False
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    # Убрать volumes для production
```

### Сборка образа

```bash
docker build -t foodcost-api:latest .
```

### Запуск production compose

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Troubleshooting

### Ошибка подключения к БД

```bash
# Проверить доступность БД
docker-compose exec api ping db

# Проверить переменные окружения
docker-compose exec api env | grep DB
```

### Ошибка подключения к Redis

```bash
# Проверить Redis
docker-compose exec redis redis-cli ping

# Должно вернуть: PONG
```

### Пересоздание контейнеров

```bash
# Полная пересборка
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Просмотр состояния

```bash
docker-compose ps
```

---

## Архитектура сети

```
┌─────────────────┐
│   foodcost_api  │───┐
│   (FastAPI)     │   │
└─────────────────┘   │
         │            │
         ▼            │
┌─────────────────┐   │ foodcost_network
│   foodcost_db   │◄──┘
│   (PostgreSQL)  │
└─────────────────┘
         ▲
         │
┌─────────────────┐
│  foodcost_redis │
│     (Redis)     │
└─────────────────┘
```

Все сервисы находятся в одной Docker network `foodcost_network` и могут общаться по именам сервисов (`db`, `redis`).

---

## Безопасность

⚠️ **Важно**: 

1. Измените пароли в `env.docker` перед deployment в production
2. Не коммитьте `.env.local` с реальными секретами в git
3. Используйте secrets management для production (Docker Secrets, Vault, etc.)

---

## Дополнительные команды

```bash
# Войти в контейнер API
docker-compose exec api bash

# Войти в контейнер БД
docker-compose exec db psql -U foodcost -d foodcost_db

# Посмотреть переменные окружения
docker-compose exec api env

# Перезапустить отдельный сервис
docker-compose restart api
```
