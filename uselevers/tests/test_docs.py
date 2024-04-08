from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_read_docs() -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "/api/v1/openapi.json" in response.text
