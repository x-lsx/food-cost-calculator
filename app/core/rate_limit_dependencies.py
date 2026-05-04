"""
Dependencies для rate limiting.

Использование:
    @app.post("/endpoint", dependencies=[Depends(rate_limit_auth)])
    async def my_endpoint():
        ...
    
    Или для кастомных лимитов:
    @app.post("/endpoint", dependencies=[Depends(get_rate_limiter_dependency("my_endpoint", 10, 60))])
    async def my_endpoint():
        ...
"""

from typing import Callable
import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer

from app.core.rate_limiter import RateLimiter, get_rate_limiter
from app.utils.dependencies import get_current_user_optional


def _get_redis_host_port():
    """Получает хост и порт Redis из переменных окружения"""
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    return host, port


def _get_rate_limiter_with_config():
    """Wrapper для get_rate_limiter с поддержкой конфигурации из env"""
    host, port = _get_redis_host_port()
    return get_rate_limiter(host=host, port=port)


# Префиксы для разных типов лимитов
RATE_LIMIT_AUTH = "auth"
RATE_LIMIT_REGISTRATION = "registration"
RATE_LIMIT_PASSWORD_RESET = "password_reset"
RATE_LIMIT_API_GENERAL = "api_general"
RATE_LIMIT_BUSINESS_OPERATIONS = "business_ops"
RATE_LIMIT_PRODUCT_CALCULATION = "product_calc"


def get_rate_limiter_dependency(
    endpoint_name: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    use_user_id: bool = False,
) -> Callable:
    """
    Factory для создания dependency rate limiter.
    
    Args:
        endpoint_name: Название эндпоинта для ключа в Redis
        max_requests: Максимальное количество запросов в окне
        window_seconds: Размер окна в секундах
        use_user_id: Если True, использовать user ID вместо IP (требует авторизации)
    
    Returns:
        Dependency функция для FastAPI
    """
    
    async def rate_limit_dependency(
        request: Request,
        rate_limiter: RateLimiter = Depends(_get_rate_limiter_with_config),
    ):
        # Определяем идентификатор: user ID или IP адрес
        if use_user_id:
            try:
                # Пытаемся получить пользователя из токена
                security = HTTPBearer(auto_error=False)
                credentials = await security(request)
                if credentials:
                    user = await get_current_user_optional(credentials, request)
                    identifier = f"user:{user.id}" if user else f"ip:{request.client.host}"
                else:
                    identifier = f"ip:{request.client.host}"
            except Exception:
                identifier = f"ip:{request.client.host}"
        else:
            identifier = f"ip:{request.client.host}"
        
        # Проверяем лимит
        is_limited = await rate_limiter.is_limited(
            identifier=identifier,
            endpoint=endpoint_name,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )
        
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Превышено количество запросов ({max_requests} за {window_seconds} сек). Повторите позже.",
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Window": str(window_seconds),
                },
            )
    
    return rate_limit_dependency


# Готовые зависимости для часто используемых сценариев

# Лимит на попытки входа (5 попыток в минуту)
rate_limit_login = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_AUTH,
    max_requests=5,
    window_seconds=60,
    use_user_id=False,  # По IP, так как пользователь еще не авторизован
)

# Лимит на регистрацию (3 регистрации в час с одного IP)
rate_limit_registration = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_REGISTRATION,
    max_requests=3,
    window_seconds=3600,
    use_user_id=False,
)

# Лимит на сброс пароля (2 запроса в 15 минут)
rate_limit_password_reset = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_PASSWORD_RESET,
    max_requests=2,
    window_seconds=900,
    use_user_id=False,
)

# Общий лимит на API (100 запросов в минуту)
rate_limit_api_general = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_API_GENERAL,
    max_requests=100,
    window_seconds=60,
    use_user_id=True,  # По user ID если авторизован
)

# Лимит на операции с бизнесом (30 операций в минуту)
rate_limit_business_ops = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_BUSINESS_OPERATIONS,
    max_requests=30,
    window_seconds=60,
    use_user_id=True,
)

# Лимит на пересчет себестоимости (10 раз в минуту)
rate_limit_product_calc = get_rate_limiter_dependency(
    endpoint_name=RATE_LIMIT_PRODUCT_CALCULATION,
    max_requests=10,
    window_seconds=60,
    use_user_id=True,
)
