from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from uselevers.tests.conftest import (  # noqa: F401,F811
    SessionTest,
    alembic_engine,
    client,
    db,
)


def sample_bill_data() -> list[dict[str, Any]]:
    return [
        {
            "total": 10.0,
            "sub_bills": [
                {"amount": 5, "reference": "REF-1"},
                {"amount": 5, "reference": "ref-2"},
            ],
        },
        {
            "total": 20.0,
            "sub_bills": [
                {"amount": 20, "reference": "INV-1"},
            ],
        },
    ]


@pytest.fixture
def create_multiple_bills(
    client: TestClient,  # noqa: F811
    db: Session,  # noqa: F811
) -> None:
    for bill in sample_bill_data():
        data = {
            "total": bill["total"],
            "sub_bills": bill["sub_bills"],
        }
        response = client.post("/api/v1/bills", json=data)
        assert response.status_code == 201
