import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings, BASE_DIR
from app.core.database import AsyncSessionLocal
from .routes import (user_routes, auth_routes, business_routes, unit_routes)
from .utils.logging import configure_logging

configure_logging(level=settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === Startup ===
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Food Cost Calculator API...")

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ Database connection: SUCCESS")
    except Exception as e:
        logger.error("❌ Database connection: FAILED", exc_info=True)
        # Можно раскомментировать, если хочешь падать при отсутствии БД
        # raise RuntimeError("Cannot connect to database") from e

    yield  # Здесь приложение работает

    # === Shutdown ===
    logger.info("🛑 Shutting down application...")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

cors_origins = [origin.strip()
                for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

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

@app.get('/')
def root():
    return {
        'message': 'Welcome to fastapi online recipe API',
        'docs': '/api/docs',
    }
