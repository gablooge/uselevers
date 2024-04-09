import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from uselevers.core import deps

from . import exceptions, models, queries, schemas

logger = logging.getLogger(__name__)

bills_router = APIRouter()


@bills_router.post("/bills", status_code=status.HTTP_201_CREATED)
async def create_bills(
    *, db: Annotated[Session, Depends(deps.get_db)], bill_data: schemas.BillSpec
) -> schemas.Bill:
    """
    Create new bill.
    """
    try:
        with db.begin():
            bill = queries.save_billspec(db, bill_data)
            return schemas.Bill.model_validate(bill, from_attributes=True)
    except IntegrityError as e:
        logger.error(f"create_bills: Duplicated reference value. Errors: {str(e)}")
        raise exceptions.ReferenceValueConflict


@bills_router.get("/bills", status_code=status.HTTP_200_OK)
def read_bills(
    reference: str | None = None,
    total_from: int | None = None,
    total_to: int | None = None,
    db: Session = Depends(deps.get_db),
) -> list[schemas.Bill]:
    """
    Get all bills.
    """
    with db.begin():
        query = db.query(models.Bill)

        if total_from is not None:
            query = query.filter(models.Bill.total >= total_from)

        if total_to is not None:
            query = query.filter(models.Bill.total <= total_to)

        # Apply filtering if reference parameter is provided
        if reference:
            # Join SubBill table to perform filtering based on reference
            query = query.join(models.Bill.sub_bills_ref)

            # Apply filtering based on reference attribute of SubBill
            query = query.filter(
                func.lower(models.SubBill.reference).ilike(func.lower(f"%{reference}%"))
            )

        # Retrieve bills based on the filtered query
        bills = query.all()

        # Filter sub-bills by reference
        for bill in bills:
            sub_bills_query = bill.sub_bills_ref
            if reference:
                sub_bills_query = sub_bills_query.filter(
                    func.lower(models.SubBill.reference).ilike(
                        func.lower(f"%{reference}%")
                    )
                )
            bill.sub_bills = sub_bills_query.all()

        return [
            schemas.Bill.model_validate(bill, from_attributes=True) for bill in bills
        ]
