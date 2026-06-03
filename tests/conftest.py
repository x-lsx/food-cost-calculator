import pytest_asyncio  # ← 1. Импортируем pytest_asyncio
import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.main import app


@pytest_asyncio.fixture(scope="function")  
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c