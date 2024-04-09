from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from uselevers.bills.models import Bill
from uselevers.tests.conftest import (  # noqa: F401,F811
    SessionTest,
    alembic_engine,
    client,
    db,
)


@pytest.mark.parametrize(
    "total,sub_bills",
    [
        (
            3,
            [
                {"amount": 1, "reference": "REF-1"},
                {"amount": 2, "reference": "ref-2"},
            ],
        ),
        (
            1,
            [
                {"amount": 1, "reference": "INV-1"},
            ],
        ),
        (
            2,
            [
                {"amount": 2},
                {"amount": 4},
            ],
        ),
    ],
)
def test_post_bill_201(
    client: TestClient,  # noqa: F811
    db: Session,  # noqa: F811
    total: float,
    sub_bills: list[dict[str, Any]],
) -> None:
    data = {
        "total": total,
        "sub_bills": sub_bills,
    }
    with db.begin():
        assert db.query(Bill).count() == 0
        response = client.post("/api/v1/bills", json=data)
        result = response.json()
        assert response.status_code == 201
        assert result["id"][0] == "B"
        assert result["total"] == total
        assert len(result["sub_bills"]) == len(sub_bills)
        assert result["created"] is not None
        assert result["updated"] is not None
        assert db.query(Bill).count() == 1


@pytest.mark.parametrize(
    "total,sub_bills,error_field,error_message",
    [
        (
            -1,
            [
                {"amount": 1, "reference": "REF-1"},
            ],
            "total",
            "Value error, Value must be a positive number or greater than or equal to 0.0",
        ),
        (
            "invalid",
            [
                {"amount": 1, "reference": "REF-1"},
            ],
            "total",
            "Input should be a valid number, unable to parse string as a number",
        ),
        (
            3,
            [
                {"amount": "invalid", "reference": "REF-1"},
            ],
            "sub_bills.0.amount",
            "Input should be a valid number, unable to parse string as a number",
        ),
        (
            9,
            [
                {"amount": -5, "reference": "REF-1"},
            ],
            "sub_bills.0.amount",
            "Value error, Value must be a positive number or greater than or equal to 0.0",
        ),
        (
            9,
            [
                {"reference": "REF-1"},
            ],
            "sub_bills.0.amount",
            "Field required",
        ),
    ],
)
def test_post_bill_422(
    client: TestClient,  # noqa: F811
    total: float,
    sub_bills: list[dict[str, Any]],
    error_field: str,
    error_message: str,
) -> None:
    data = {
        "total": total,
        "sub_bills": sub_bills,
    }
    response = client.post("/api/v1/bills", json=data)
    assert response.status_code == 422
    result = response.json()
    assert result["detail"]["errors"][error_field][0] == error_message


def test_post_bill_422_missing_total(
    client: TestClient,  # noqa: F811
) -> None:
    data = {
        "sub_bills": [
            {"amount": 1, "reference": "REF-1"},
        ],
    }
    response = client.post("/api/v1/bills", json=data)
    assert response.status_code == 422
    result = response.json()
    assert result["detail"]["errors"]["total"][0] == "Field required"


def test_post_bill_422_missing_subbills(
    client: TestClient,  # noqa: F811
) -> None:
    data = {
        "total": 6,
    }
    response = client.post("/api/v1/bills", json=data)
    assert response.status_code == 422
    result = response.json()
    assert result["detail"]["errors"]["sub_bills"][0] == "Field required"


def test_post_bill_422_empty_subbills(
    client: TestClient,  # noqa: F811
) -> None:
    data = {
        "total": 6,
        "sub_bills": [],
    }
    response = client.post("/api/v1/bills", json=data)
    assert response.status_code == 422
    result = response.json()
    assert (
        result["detail"]["errors"]["sub_bills"][0]
        == "Value error, At least one sub bill is required"
    )


def test_post_bill_422_invalid_reference(
    client: TestClient,  # noqa: F811
) -> None:
    data = {
        "total": 6,
        "sub_bills": [
            {"amount": 1, "reference": "REF-1"},
            {"amount": 2, "reference": "ref-1"},
        ],
    }
    response = client.post("/api/v1/bills", json=data)
    assert response.status_code == 409
    result = response.json()
    assert (
        result["detail"]["errors"]["reference"][0]
        == "Bill reference value already exists. Please select another value."
    )
