import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from uselevers.core import deps

from . import exceptions, queries, schemas

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
            return schemas.Bill.model_validate(
                queries.save_billspec(db, bill_data), from_attributes=True
            )
    except IntegrityError as e:
        logger.error(f"create_bills: Duplicated reference value. Errors: {str(e)}")
        raise exceptions.ReferenceValueConflict
