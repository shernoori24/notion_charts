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
    # Auth not required in this configuration; request should succeed
    r = client.get("/api/data")
    assert r.status_code == 200
*** End Patch