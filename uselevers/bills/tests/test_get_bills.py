from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from uselevers.tests.conftest import (  # noqa: F401,F811
    SessionTest,
    alembic_engine,
    client,
    db,
)

from .fixtures import create_multiple_bills  # noqa: F401,F811


def test_get_bills_200(
    client: TestClient,  # noqa: F811
    db: Session,  # noqa: F811
    create_multiple_bills: None,  # noqa: F811
) -> None:
    with db.begin():
        # test get all bills
        response = client.get("/api/v1/bills")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2


def test_get_bills_filtered_by_reference(
    client: TestClient,  # noqa: F811
    db: Session,  # noqa: F811
    create_multiple_bills: None,  # noqa: F811
) -> None:
    with db.begin():
        # test get filtered reference by `ref-1`
        response = client.get("/api/v1/bills?reference=ref-1")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert len(result[0]["sub_bills"]) == 1
        assert result[0]["sub_bills"][0]["reference"] == "REF-1"

        # test get filtered reference by `ref`
        response = client.get("/api/v1/bills?reference=ref")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert len(result[0]["sub_bills"]) == 2

        # test get filtered reference by `in`
        response = client.get("/api/v1/bills?reference=in")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert len(result[0]["sub_bills"]) == 1
        assert result[0]["sub_bills"][0]["reference"] == "INV-1"


def test_get_bills_filtered_by_total_from(
    client: TestClient,  # noqa: F811
    db: Session,  # noqa: F811
    create_multiple_bills: None,  # noqa: F811
) -> None:
    with db.begin():
        # test get filtered total_from by `0`
        response = client.get("/api/v1/bills?total_from=0")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2

        # test get filtered total_from by `10`
        response = client.get("/api/v1/bills?total_from=10")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2

        # test get filtered total_from by `20`
        response = client.get("/api/v1/bills?total_from=20")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["sub_bills"][0]["reference"] == "INV-1"


def test_get_bills_filtered_by_total_to(
    client: TestClient,  # noqa: F811
    db: Session,  # noqa: F811
    create_multiple_bills: None,  # noqa: F811
) -> None:
    with db.begin():
        # test get filtered total_to by `0`
        response = client.get("/api/v1/bills?total_to=0")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

        # test get filtered total_to by `10`
        response = client.get("/api/v1/bills?total_to=10")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["sub_bills"][0]["reference"] == "REF-1"

        # test get filtered total_to by `20`
        response = client.get("/api/v1/bills?total_to=20")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2
