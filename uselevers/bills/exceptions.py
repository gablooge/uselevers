from fastapi import HTTPException, status

from uselevers.core.exceptions import HTTPExceptionExtra, HTTPSimpleError


class ReferenceValueConflict(HTTPException, HTTPExceptionExtra):
    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=HTTPSimpleError(
                message="Bill reference conflict",
                errors={
                    "reference": [
                        "Bill reference value already exists. "
                        "Please select another value."
                    ]
                },
            ).model_dump(),
        )

    model = HTTPSimpleError
    status_code = status.HTTP_409_CONFLICT
    examples = {
        "detail": {
            "message": "Bill reference conflict",
            "errors": {
                "reference": [
                    "Bill reference value already exists. Please select another value."
                ]
            },
        }
    }
