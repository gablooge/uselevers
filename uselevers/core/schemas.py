from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class MixinCreatedUpdated(BaseModel):
    created: Annotated[datetime, Field(description="Created at")]
    updated: Annotated[datetime, Field(description="Updated at")]
