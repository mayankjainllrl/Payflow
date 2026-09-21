import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.core.db import get_session
from app.models.payment import Base

TEST_DB_URL = "postgresql+asyncpg://payflow:payflow@localhost:5432/payflow_test"

@pytest_asyncio.fixture
async def async_client():
    engine = create_async_engine(TEST_DB_URL)
    TestSession = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async def override_get_session():
        async with TestSession() as session:
            yield session
    app.dependency_overrides[get_session] = override_get_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
        
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()