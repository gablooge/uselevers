import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import deps

logger = logging.getLogger(__name__)

healthcheck_router = APIRouter()


class Health(BaseModel):
    db: bool = False


@healthcheck_router.get("/health")
async def health(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    response: Response,
) -> Health:
    """
    Perform internal health checks
    """
    health = Health()

    try:
        with db.begin():
            db.execute(text("SELECT 1"))
            health.db = True
    except Exception as e:
        logger.warning(f"health > checking database failing > {e}")

    if not health.db:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health
