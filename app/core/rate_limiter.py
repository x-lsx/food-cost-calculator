from contextlib import asynccontextmanager
from functools import lru_cache
from time import time
import random
from typing import Optional

from redis.asyncio import Redis
from fastapi import FastAPI


class RedisManager:
    """Менеджер подключения к Redis"""
    
    _instance: Optional[Redis] = None
    
    @classmethod
    def get_redis(cls, host: str = "localhost", port: int = 6379) -> Redis:
        if cls._instance is None:
            cls._instance = Redis(
                host=host,
                port=port,
                decode_responses=True,
            )
        return cls._instance
    
    @classmethod
    async def ping(cls) -> bool:
        try:
            await cls.get_redis().ping()
            return True
        except Exception:
            return False
    
    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.aclose()
            cls._instance = None


class RateLimiter:
    """
    Rate limiter на основе Redis с использованием Lua-скриптов для атомарности.
    
    Использует sorted sets (ZSET) для хранения временных меток запросов.
    """
    
    def __init__(self, redis: Redis):
        self._redis = redis
        self._lua_sha: Optional[str] = None
        
    async def _load_script(self) -> str:
        """Загружает Lua-скрипт в Redis и кэширует его SHA"""
        if self._lua_sha is None:
            script = """
            -- KEYS[1] = ключ rate limiter
            -- ARGV[1] = текущее время (ms)
            -- ARGV[2] = начало окна (ms)
            -- ARGV[3] = максимальное количество запросов
            -- ARGV[4] = время жизни ключа (секунды)
            -- ARGV[5] = уникальный ID запроса
            
            -- Удаляем старые записи за пределами окна
            redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, ARGV[2])
            
            -- Считаем текущее количество запросов в окне
            local count = redis.call("ZCARD", KEYS[1])
            
            -- Если лимит превышен, возвращаем 1 (limited)
            if count >= tonumber(ARGV[3]) then
                return 1
            end
            
            -- Добавляем текущий запрос
            redis.call("ZADD", KEYS[1], ARGV[1], ARGV[5])
            
            -- Устанавливаем TTL для ключа
            redis.call("EXPIRE", KEYS[1], ARGV[4])
            
            -- Возвращаем 0 (not limited)
            return 0
            """
            self._lua_sha = await self._redis.script_load(script)
        
        return self._lua_sha

    async def is_limited(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """
        Проверяет, превышен ли лимит запросов.
        
        Args:
            identifier: Уникальный идентификатор (обычно IP адрес или user ID)
            endpoint: Название эндпоинта для разделения лимитов
            max_requests: Максимальное количество запросов в окне
            window_seconds: Размер окна в секундах
            
        Returns:
            True если лимит превышен, False если запрос разрешен
        """
        lua_sha = await self._load_script()
        
        key = f"rate_limiter:{endpoint}:{identifier}"
        current_ms = int(time() * 1000)
        window_start_ms = current_ms - window_seconds * 1000
        member_id = f"{current_ms}-{random.randint(0, 100_000)}"
        
        result = await self._redis.evalsha(
            lua_sha,
            1,  # количество ключей
            key,
            current_ms,
            window_start_ms,
            max_requests,
            window_seconds,
            member_id,
        )
        
        return result == 1
    
    async def get_remaining_requests(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    ) -> int:
        """
        Возвращает количество оставшихся запросов в текущем окне.
        Полезно для добавления заголовков ответа.
        """
        key = f"rate_limiter:{endpoint}:{identifier}"
        current_ms = int(time() * 1000)
        window_start_ms = current_ms - window_seconds * 1000
        
        # Удаляем старые записи
        await self._redis.zremrangebyscore(key, 0, window_start_ms)
        
        # Считаем текущее количество
        current_count = await self._redis.zcard(key)
        
        return max(0, max_requests - current_count)


@lru_cache
def get_rate_limiter(host: str = "localhost", port: int = 6379) -> RateLimiter:
    """Factory для получения экземпляра RateLimiter"""
    return RateLimiter(RedisManager.get_redis(host=host, port=port))


async def check_redis_connection() -> bool:
    """Проверка подключения к Redis"""
    return await RedisManager.ping()
