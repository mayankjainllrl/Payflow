from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_database_url_is_valid():
    from sqlalchemy.ext.asyncio import create_async_engine
    create_async_engine(settings.database_url)
        
