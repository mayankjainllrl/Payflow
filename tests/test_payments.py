
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_missing_idempotency_key_is_rejected():
    r = client.post("/payments", json={"amount_cents": 5000})
    assert r.status_code == 422                 
    
    
def test_invalid_amount_is_rejected():
    r = client.post(
        "/payments",
        json={"amount_cents": "abc"},
        headers={"Idempotency-Key": "test-invalid"}
        )
    assert r.status_code == 422

async def test_same_key_returns_same_payment(async_client):
    key = str(uuid.uuid4())
    body = {"amount_cents": 5000}
    r1 = await async_client.post("/payments", json=body, headers={"Idempotency-Key": key})
    r2 = await async_client.post("/payments", json=body, headers={"Idempotency-Key": key})
    assert r1.status_code == 201
    assert r1.json()["id"] == r2.json()["id"] 