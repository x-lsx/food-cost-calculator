from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker 
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from contextlib import asynccontextmanager
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
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        
        
@asynccontextmanager
async def lifespan(app):
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