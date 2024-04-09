from typing import Annotated

from pydantic import BaseModel, Field, validator

from uselevers.core.models import id_len
from uselevers.core.schemas import MixinCreatedUpdated


def check_positive_value(value: float) -> float:
    if isinstance(value, float) and value < 0:
        raise ValueError(
            "Value must be a positive number or greater than or equal to 0.0"
        )
    return value


class SubBillSpec(BaseModel):
    amount: float
    reference: str | None = None

    @validator("amount")
    def check_amount(cls, value: float) -> float:
        return check_positive_value(value)


class BillSpec(BaseModel):
    total: Annotated[float, Field(description="Total")]
    sub_bills: list[SubBillSpec]

    @validator("total")
    def check_total(cls, value: float) -> float:
        # TODO: validate total should be equal with the total of sub_bill amounts
        return check_positive_value(value)

    @validator("sub_bills")
    def check_sub_bills(cls, value: list[SubBillSpec]) -> list[SubBillSpec]:
        if not value:
            raise ValueError("At least one sub bill is required")
        return value


class Bill(MixinCreatedUpdated, BillSpec, BaseModel):
    id: Annotated[
        str,
        Field(
            description="Bill ID",
            max_length=id_len,
        ),
    ]
