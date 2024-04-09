from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict


class HTTPSimpleError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str
    errors: dict[str, list[str]]


class HTTPExceptionExtra(Protocol):
    """
    Implement this protocol to use build_exception_responses on the exception.
    Most user errors should implement this protocol.
    """

    status_code: int
    """
    HTTP status code to return
    """
    examples: dict[str, Any]
    """
    Examples to attach
    """
    model: type[BaseModel] = HTTPSimpleError
    """
    Model that "detail" should follow
    """
