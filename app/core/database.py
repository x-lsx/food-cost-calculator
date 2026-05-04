from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker 
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional

from .config import settings


engine = create_async_engine(settings.DB_URL, echo = False, future = True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit = False,
    autoflush = False,
    autocommit = False
)

class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД.
    
    Важно: больше не делает автокоммит! Коммит должен вызываться явно в сервисах
    там, где это необходимо для контроля границ транзакций.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        # Убран автокоммит - теперь коммит вызывается явно в сервисах
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def lifespan(app):
    """
    Lifespan контекст для проверки подключения к БД при старте приложения.
    
    Использование:
        app = FastAPI(lifespan=lifespan)
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print("✅ PostgreSQL подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        raise
    
    yield
    
    await engine.dispose()
    print("🔌 PostgreSQL отключен")