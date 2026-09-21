import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api_server import database, main


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=engine))
    monkeypatch.setattr(main, "SessionLocal", database.SessionLocal)
    database.Base.metadata.create_all(bind=engine)
    with TestClient(main.app) as c:
        yield c


PAYLOAD = {
    "frame_id": 7,
    "persons": [
        {"id": 0, "bbox": [1, 2, 3, 4], "events": ["hand_raise", "standing"], "engagement_score": 50.0}
    ],
}


def test_update_persists_rows_and_broadcasts(client):
    with client.websocket_connect("/ws/analytics") as ws:
        assert client.post("/stream/update", json=PAYLOAD).json() == {"status": "ok"}
        assert ws.receive_json()["persons"][0]["events"] == ["hand_raise", "standing"]

    db = database.SessionLocal()
    try:
        assert db.query(database.BehaviorEvent).count() == 2
        assert db.query(database.EngagementMetric).count() == 1
    finally:
        db.close()


def test_malformed_update_is_rejected(client):
    assert client.post("/stream/update", json={"frame_id": 1, "persons": [{"id": 0}]}).status_code == 422
    assert client.post("/stream/update", json={"persons": []}).status_code == 422
