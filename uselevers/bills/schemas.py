from typing import Annotated

from pydantic import BaseModel, Field

from uselevers.core.models import id_len
from uselevers.core.schemas import MixinCreatedUpdated


class BillSpec(BaseModel):
    total: Annotated[float, Field(description="Total")]


class Bill(MixinCreatedUpdated, BillSpec, BaseModel):
    id: Annotated[
        str,
        Field(
            description="Bill ID",
            max_length=id_len,
        ),
    ]
