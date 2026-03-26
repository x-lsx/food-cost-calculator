from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, BASE_DIR
from app.routes import (user_routes, auth_routes, business_routes)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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

@app.get('/')
def root():
    return {
        'message': 'Welcome to fastapi online recipe API',
        'docs': '/api/docs',
    }
