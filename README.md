# Food Cost Calculator API 🍽️

**Мощный REST API для расчета себестоимости блюд и управления меню ресторана**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org)

---

## 📋 Содержание

- [Немного о проекте](#немного-о-проекте)
- [Возможности](#возможности)
- [Технологический стек](#технологический-стек)
- [Предварительные требования](#предварительные-требования)
- [Быстрый старт](#быстрый-старт)
- [Запуск в Docker](#запуск-в-docker)
- [Структура проекта](#структура-проекта)
- [API Документация](#api-документация)
- [Разработка](#разработка)

---

## 🎯 Немного о проекте

**Food Cost Calculator** — это веб-приложение на FastAPI, разработанное для автоматизации расчетов себестоимости блюд и управления меню в ресторанах и кафе. 

Приложение позволяет:
- 📊 Управлять каталогом ингредиентов с текущими ценами
- 🧮 Автоматически рассчитывать себестоимость каждого блюда
- 💰 Отслеживать изменение цен и их влияние на прибыль
- 🔐 Управлять пользователями и правами доступа
- ⚡ Быстро обрабатывать запросы благодаря кэшированию

---

## ✨ Возможности

- ✅ **Управление ингредиентами** — добавляйте, обновляйте и удаляйте ингредиенты с указанием цены за единицу
- ✅ **Управление рецептами** — создавайте рецепты с перечислением компонентов и их количества
- ✅ **Автоматический расчет цены** — система автоматически рассчитывает себестоимость на основе текущих цен ингредиентов
- ✅ **Аналитика** — просматривайте статистику по популярным блюдам и трендам цен
- ✅ **Кэширование** — Redis обеспечивает высокую скорость ответов
- ✅ **Аутентификация** — JWT-токены для безопасного доступа к API
- ✅ **Миграции БД** — Alembic для версионирования схемы базы данных
- ✅ **Тестирование** — встроенная поддержка pytest и asyncio

---

## 🛠 Технологический стек

### Backend
- **FastAPI** (0.121.1) — современный фреймворк для создания REST API
- **Uvicorn** (0.38.0) — ASGI сервер для запуска приложения
- **Python** (3.12) — язык программирования

### База данных
- **PostgreSQL** (15-alpine) — основная база данных
- **SQLAlchemy** (2.0.44) — ORM для работы с БД
- **Alembic** (1.14.0) — инструмент для миграций БД
- **asyncpg** (0.30.0) — асинхронный драйвер PostgreSQL

### Кэширование
- **Redis** (7-alpine) — для кэширования и сессий

### Безопасность
- **Pydantic** (2.12.4) — валидация данных
- **python-jose** (3.5.0) — работа с JWT токенами
- **passlib** (1.7.4) + **bcrypt** (3.2.2) — хеширование паролей

### Тестирование
- **pytest** (9.0.3) — фреймворк для тестирования
- **pytest-asyncio** (1.4.0) — поддержка асинхронного кода в тестах

### DevOps
- **Docker** & **Docker Compose** — контейнеризация
- **python-dotenv** (1.2.1) — управление переменными окружения

---

## 📦 Предварительные требования

Для локальной разработки вам потребуется:

- **Python** 3.12 или выше
- **pip** — менеджер пакетов Python
- **PostgreSQL** 15 или выше
- **Redis** 7 или выше

**Для Docker:**
- **Docker** 20.10+
- **Docker Compose** 2.0+

---

## 🚀 Быстрый старт

### 1️⃣ Клонируйте репозиторий

```bash
git clone https://github.com/x-lsx/food-cost-calculator.git
cd food-cost-calculator
```

### 2️⃣ Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # на Windows: venv\Scripts\activate
```

### 3️⃣ Установите зависимости

```bash
pip install -r requirements.txt
```

### 4️⃣ Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/foodcost
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=foodcost

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# JWT
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
DEBUG=True
ENVIRONMENT=development
```

### 5️⃣ Запустите миграции БД

```bash
alembic upgrade head
```

### 6️⃣ Запустите сервер разработки

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: **http://localhost:8000**

📚 Интерактивная документация API: **http://localhost:8000/api/docs** (Swagger UI)

---

## 🐳 Запуск в Docker

### Docker Compose

```bash
# Создайте файл .env.docker
cp .env.example .env.docker

# Запустите контейнеры
docker-compose up -d
```

Приложение будет доступно по адресу: **http://localhost:8000**


### Остановка

```bash
docker-compose down

# С удалением данных
docker-compose down -v
```

---

## 📁 Структура проекта

```
food-cost-calculator/
├── app/
│   ├── core/              # Конфигурация, константы, исключения
│   ├── models/            # SQLAlchemy модели БД
│   ├── schemas/           # Pydantic схемы для валидации
│   ├── routes/            # API endpoints
│   ├── services/          # Бизнес-логика
│   ├── repositories/      # Работа с БД
│   ├── utils/             # Утилиты и вспомогательные функции
│   └── main.py            # Точка входа приложения
├── migrations/            # Alembic миграции БД
├── tests/                 # Тесты
├── docker-compose.yml     # Конфигурация Docker
├── Dockerfile             # Инструкции для сборки образа
├── requirements.txt       # Зависимости Python
├── alembic.ini           # Конфигурация Alembic
└── README.md             # Этот файл
```

---

## 📖 API Документация

### Интерактивная документация

Запустив приложение, откройте в браузере:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Запустить все тесты
pytest

# С подробным выводом
pytest -v


```

### Написание тестов

Тесты находятся в директории `tests/` и организованы по структуре основного приложения.

---

## 🔧 Разработка

### Установка зависимостей разработчика

```bash
pip install -r requirements.txt
```

### Создание новой миграции БД

```bash
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат последней миграции

```bash
alembic downgrade -1
```

### Форматирование кода

```bash
# Используя встроенные возможности
python -m black app/
```

---

## 📝 Переменные окружения

| Переменная | Описание | Пример |
|-----------|---------|--------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://user:pass@localhost/db` |
| `REDIS_URL` | URL подключения к Redis | `redis://localhost:6379` |
| `SECRET_KEY` | Секретный ключ для JWT | `your-secret-key` |
| `ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена (минуты) | `30` |
| `DEBUG` | Режим отладки | `True` / `False` |
| `ENVIRONMENT` | Окружение | `development` / `production` |

---

## 🎓 Дополнительные ресурсы

- [FastAPI документация](https://fastapi.tiangolo.com)
- [SQLAlchemy документация](https://docs.sqlalchemy.org)
- [PostgreSQL документация](https://www.postgresql.org/docs)
- [Redis документация](https://redis.io/documentation)
- [Alembic документация](https://alembic.sqlalchemy.org)

---
