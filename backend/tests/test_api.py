from fastapi.testclient import TestClient
import pandas as pd

from backend.app import app
import database_client

client = TestClient(app)


def fake_get_notion_data():
    df = pd.DataFrame([
        {"Category": "A", "Value": 10},
        {"Category": "B", "Value": 20},
        {"Category": "C", "Value": 30},
    ])
    return df


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_get_data(monkeypatch):
    monkeypatch.setattr(database_client, "get_notion_data", fake_get_notion_data)
    r = client.get("/api/data")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 3
    assert isinstance(body["results"], list)


def test_api_key_required(monkeypatch):
    monkeypatch.setattr(database_client, "get_notion_data", fake_get_notion_data)
    # set an API key in environment for the app
    import os
    os.environ["API_KEY"] = "secret"
    # re-import app var to pick up env change would be complex; instead, call route with header and without
    r = client.get("/api/data")
    # With environment variable set (in the running process), the app requires key and returns 401
    # Since our TestClient uses the same process, we expect 401
    assert r.status_code == 401
    r2 = client.get("/api/data", headers={"x-api-key": "secret"})
    assert r2.status_code == 200
*** End Patch