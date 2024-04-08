from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from uselevers.bills.models import Bill
from uselevers.bills.schemas import BillSpec
from uselevers.core import deps
from uselevers.tests.conftest import SessionTest, alembic_engine, db  # noqa: F401,F811


@pytest.mark.parametrize(
    "total",
    [
        (0),
        (0.5),
        (1.00),
        (1.05),
    ],
)
def test_crud_bills(
    db: Annotated[Session, Depends(deps.get_db)],  # noqa: F811
    total: float,
) -> None:
    bill_create = BillSpec(
        total=total,
    )
    with db.begin():
        # test create
        assert db.query(Bill).count() == 0
        instance = Bill(**jsonable_encoder(bill_create))
        db.add(instance)
        # write the object to the database
        db.flush()
        assert db.query(Bill).count() == 1

        # test read
        created_bill = db.query(Bill).filter(Bill.id == instance.id).first()
        assert created_bill is not None
        assert created_bill.total == total
        assert created_bill.id[0] == "B"

        # test update with invalid total
        with pytest.raises(IntegrityError):
            created_bill.total = -1
            db.flush()

    # test update and delete
    with db.begin():
        created_bill = db.query(Bill).first()
        # test update with valid total
        new_total: float = 1.10
        created_bill.total = new_total
        db.flush()
        updated_bill = db.query(Bill).filter(Bill.id == created_bill.id).first()
        assert updated_bill is not None
        assert updated_bill.total == new_total
        assert updated_bill.id[0] == "B"

        # test delete
        db.delete(updated_bill)
        db.flush()
        assert db.query(Bill).count() == 0


def test_create_bill_with_invalid_total(
    db: Annotated[Session, Depends(deps.get_db)],  # noqa: F811
):
    bill_create = BillSpec(
        total=-1,
    )
    with db.begin():
        # test create
        assert db.query(Bill).count() == 0
        with pytest.raises(IntegrityError):
            instance = Bill(**jsonable_encoder(bill_create))
            db.add(instance)
            db.flush()

    with db.begin():
        assert db.query(Bill).count() == 0
