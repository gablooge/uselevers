import logging
import sys
import time
import typing
from collections import defaultdict
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from alembic.command import upgrade
from alembic.config import Config
from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError

from uselevers.bills.views import bills_router
from uselevers.core.config import log_level_from, settings
from uselevers.core.healthcheck import healthcheck_router

# Set up global logger configuration


logging.basicConfig(
    level=log_level_from(settings),
    format="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",
)
# Reduce logging level of some libraries. Comment out temporarily to get more detailed
# logs
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)


# Local logger


logger = logging.getLogger(__name__)


# Attach lifespan manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.AsyncIterator[None]:
    # Development helpers
    # Do not add any production helpers here

    if settings.DEV_MIGRATIONS:
        logger.debug(f"Settings: {settings}")
        logger.info("Performing Alembic upgrade to head...")
        upgrade(Config(settings.DEV_MIGRATIONS_ALEMBIC_INI), "head")
        logger.info("Completed all migrations...")

    yield None


# Create app

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_PATH}/openapi.json",
    lifespan=lifespan,
    debug=settings.DEV_FASTAPI_DEBUG,
    servers=[
        {"url": "/", "description": ""},
    ],
    swagger_ui_parameters={
        "persistAuthorization": True,
        "requestSnippetsEnabled": True,
        "displayOperationId": True,
    },
)

# Global exception handlers


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception) -> None:
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)
    logger.error(
        f"Handler: {request.method} {request.url} "
        f"{exception_name} {exception_value} {exception_traceback}"
    )


@app.exception_handler(ValidationError)
@app.exception_handler(RequestValidationError)
async def custom_validation_error(
    request: Request, exc: ValidationError
) -> JSONResponse:
    reformatted_message: typing.Any = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(map(str, filtered_loc))
        reformatted_message[field_string].append(msg)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {"detail": {"message": "Invalid request", "errors": reformatted_message}}
        ),
    )


# Global middleware


@app.middleware("http")
async def swagger_inject_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    if app.docs_url and request.url.path.startswith(app.docs_url):
        response = await call_next(request)
        if isinstance(response, StreamingResponse):
            body = b""
            async for chunk in response.body_iterator:
                if isinstance(chunk, str):
                    body += chunk.encode(response.charset)
                else:
                    body += chunk
        else:
            body = response.body

        return HTMLResponse(
            content=body,
            status_code=response.status_code,
            media_type=response.media_type,
        )
    response = await call_next(request)
    return response


@app.middleware("http")
async def log_request_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f"{request.method} {request.url} {response.status_code} {process_time}s"
    )
    return response


# CORS middleware


origins = [str(settings.CORS_ORIGIN_FRONTEND).strip("/")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization"],
)

# Attach routes


app.include_router(bills_router, prefix=settings.API_V1_PATH)
app.include_router(healthcheck_router, tags=["Internal"])


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.

    See https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#openapi-operationid
    """  # noqa: E501
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)
