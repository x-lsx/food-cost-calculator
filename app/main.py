import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.database import AsyncSessionLocal, lifespan as db_lifespan
from app.core.rate_limiter import RedisManager, check_redis_connection
from app.core.config import BASE_DIR, settings


from .routes import auth_routes, business_routes, unit_routes, user_routes
from .utils.logging import configure_logging

configure_logging(level=int(settings.LOG_LEVEL))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Объединенный lifespan контекст для БД и Redis.

    Последовательность:
    1. Подключение к PostgreSQL
    2. Подключение к Redis
    3. Работа приложения
    4. Отключение Redis
    5. Отключение PostgreSQL
    """
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Food Cost Calculator API...")

    # === PostgreSQL ===
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ Database connection: SUCCESS")
    except Exception as e:
        logger.error("❌ Database connection: FAILED", exc_info=True)
        raise RuntimeError("Cannot connect to database") from e

    # === Redis ===
    try:
        redis_available = await check_redis_connection()
        if redis_available:
            logger.info("✅ Redis connection: SUCCESS")
        else:
            logger.warning("⚠️ Redis connection: FAILED (rate limiting disabled)")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection: FAILED ({e}) - rate limiting disabled")

    yield  # Здесь приложение работает

    # === Shutdown ===
    logger.info("🛑 Shutting down application...")

    # Отключаем Redis
    try:
        await RedisManager.close()
        logger.info("🔌 Redis disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Redis: {e}")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger = logging.getLogger(__name__)
#     logger.info("Starting Food Cost Calculator API...")
#     try:
#         async with AsyncSessionLocal() as session:
#             await session.execute(text("SELECT 1"))
#         logger.info("Database connection: SUCCESS")
#     except Exception:
#         logger.error("Database connection: FAILED", exc_info=True)
#     yield
#     logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

cors_origins = [
    origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = BASE_DIR / settings.UPLOAD_DIR
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(business_routes.router)
app.include_router(unit_routes.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to fastapi online recipe API",
        "docs": "/api/docs",
    }
