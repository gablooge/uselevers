from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["db"] is True
