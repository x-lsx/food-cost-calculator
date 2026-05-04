# Rate Limiting в Food Cost Calculator API

## Обзор

В проект добавлена система rate limiting на основе Redis с использованием Lua-скриптов для атомарности операций.

## Архитектура

```
app/core/
├── rate_limiter.py              # Ядро системы (RateLimiter класс + RedisManager)
└── rate_limit_dependencies.py   # Factory и готовые зависимости для FastAPI

app/utils/
└── dependencies.py              # Добавлен get_current_user_optional()
```

## Как это работает

### 1. **RateLimiter** (`app/core/rate_limiter.py`)

Использует Redis Sorted Sets (ZSET) для хранения временных меток запросов:
- Ключ: `rate_limiter:{endpoint}:{identifier}`
- Identifier: IP адрес или user ID
- Lua-скрипт обеспечивает атомарность проверки и обновления

```python
# Пример использования напрямую
from app.core.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
is_limited = await limiter.is_limited(
    identifier="192.168.1.1",
    endpoint="auth",
    max_requests=5,
    window_seconds=60,
)
```

### 2. **Готовые зависимости** (`app/core/rate_limit_dependencies.py`)

Factory функция создает dependency для FastAPI:

```python
from app.core.rate_limit_dependencies import get_rate_limiter_dependency

# Создать зависимость с кастомными параметрами
my_rate_limit = get_rate_limiter_dependency(
    endpoint_name="my_endpoint",
    max_requests=10,
    window_seconds=60,
    use_user_id=True,  # Использовать user ID вместо IP если авторизован
)

@app.post("/my-endpoint", dependencies=[Depends(my_rate_limit)])
async def my_endpoint():
    ...
```

### 3. **Предустановленные лимиты**

В модуле уже определены готовые зависимости:

| Зависимость | Лимит | Окно | Идентификатор |
|-------------|-------|------|---------------|
| `rate_limit_login` | 5 запросов | 60 сек | IP |
| `rate_limit_registration` | 3 запроса | 3600 сек | IP |
| `rate_limit_password_reset` | 2 запроса | 900 сек | IP |
| `rate_limit_api_general` | 100 запросов | 60 сек | User ID (если авторизован) |
| `rate_limit_business_ops` | 30 запросов | 60 сек | User ID |
| `rate_limit_product_calc` | 10 запросов | 60 сек | User ID |

## Подключение к роутам

### Пример 1: Auth endpoints

```python
# app/routes/auth_routes.py
from app.core.rate_limit_dependencies import rate_limit_login, rate_limit_registration

@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_login)],
)
async def login_for_access_token(...):
    ...

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_registration)],
)
async def register(...):
    ...
```

### Пример 2: Product Ingredients endpoints

```python
# app/routes/product_ingredient_routes.py
from app.core.rate_limit_dependencies import rate_limit_business_ops, rate_limit_product_calc

@router.post(
    "/",
    dependencies=[Depends(rate_limit_business_ops)],
)
async def create_product_ingredient(...):
    ...

@router.patch(
    "/{id}",
    dependencies=[Depends(rate_limit_product_calc)],
)
async def update_product_ingredient(...):
    ...
```

## Ответ при превышении лимита

```json
HTTP 429 Too Many Requests
{
    "detail": "Превышено количество запросов (5 за 60 сек). Повторите позже."
}
```

Заголовки ответа:
```
Retry-After: 60
X-RateLimit-Limit: 5
X-RateLimit-Window: 60
```

## Интеграция с lifespan

В `app/main.py` добавлена проверка подключения к Redis при старте:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... проверка PostgreSQL ...
    
    # Проверка Redis
    try:
        redis_available = await check_redis_connection()
        if redis_available:
            logger.info("✅ Redis connection: SUCCESS")
        else:
            logger.warning("⚠️ Redis connection: FAILED (rate limiting disabled)")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection: FAILED ({e}) - rate limiting disabled")
    
    yield
    
    # Отключение Redis при shutdown
    await RedisManager.close()
```

## Требования

### Redis

Необходим Redis сервер. Для локальной разработки:

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

Или через docker-compose:

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Python зависимости

```bash
pip install redis
```

Уже добавлено в `requirements.txt`.

## Конфигурация

Redis подключается к `localhost:6379` по умолчанию. Для изменения отредактируйте:

```python
# app/core/rate_limiter.py
class RedisManager:
    @classmethod
    def get_redis(cls) -> Redis:
        if cls._instance is None:
            cls._instance = Redis(
                host="localhost",  # Изменить здесь
                port=6379,         # Изменить здесь
                decode_responses=True,
            )
        return cls._instance
```

В будущем можно вынести в `settings.py`.

## Безопасность

### Почему Lua-скрипт?

Метод `is_limited_video()` использует pipeline, который **НЕ атомарен**:
```python
# ⚠️ НЕ ИСПОЛЬЗОВАТЬ для production!
async with self._redis.pipeline() as pipe:
    await pipe.zremrangebyscore(...)
    await pipe.zcard(...)  # Может измениться между вызовами!
    await pipe.zadd(...)
    await pipe.execute()
```

Метод `is_limited()` использует Lua-скрипт, который выполняется **атомарно**:
```python
# ✅ Правильный вариант
result = await self._redis.evalsha(lua_sha, 1, key, ...)
```

### Защита от race conditions

Lua-скрипт гарантирует, что между проверкой количества запросов и добавлением нового нет других операций.

## Мониторинг

Для отслеживания rate limiting можно использовать:

1. **Логи приложения** - предупреждения при отказе Redis
2. **Redis CLI**:
   ```bash
   redis-cli KEYS "rate_limiter:*"
   redis-cli ZCARD "rate_limiter:auth:192.168.1.1"
   ```
3. **Заголовки ответа** - X-RateLimit-* для клиента

## Расширение

### Добавить новый лимит

```python
# app/core/rate_limit_dependencies.py

RATE_LIMIT_MY_FEATURE = "my_feature"

rate_limit_my_feature = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_MY_FEATURE,
    max_requests=20,
    window_seconds=120,
    use_user_id=True,
)

# Использование в роуте
@router.post("/my-feature", dependencies=[Depends(rate_limit_my_feature)])
async def my_feature():
    ...
```

### Кастомная логика идентификатора

Если нужна сложная логика определения идентификатора (например, по API ключу):

```python
async def custom_rate_limit_dependency(request: Request, ...):
    # Ваша логика получения identifier
    api_key = request.headers.get("X-API-Key")
    identifier = f"api_key:{api_key}" if api_key else f"ip:{request.client.host}"
    
    is_limited = await rate_limiter.is_limited(...)
    ...
```

## Troubleshooting

### Redis не доступен

Приложение продолжит работу, но rate limiting будет отключен. В логах:
```
⚠️ Redis connection: FAILED (Connection refused) - rate limiting disabled
```

### Слишком строгий лимит

Увеличьте `max_requests` или `window_seconds` в соответствующей зависимости.

### Ложные срабатывания при NAT

Если несколько пользователей за одним NAT (офис, мобильная сеть), используйте `use_user_id=True` для идентификации по токену.

## Тестирование

```bash
# Быстро превысить лимит login (5 запросов в минуту)
for i in {1..10}; do
    curl -X POST http://localhost:8000/api/v1/auth/login \
        -d "username=test@example.com&password=wrong"
done
```

После 5-го запроса получите HTTP 429.
