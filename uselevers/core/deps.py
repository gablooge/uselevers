import typing
from typing import TypeAlias

import httpx
from fastapi import Request
from sqlalchemy import orm

from uselevers.core.config import settings
from uselevers.core.db import SessionLocal

# common


def get_db() -> typing.Generator[orm.Session, None, None]:
    # with SessionLocal(autobegin=False) as session:
    with SessionLocal() as session:
        yield session


# api


# Assign a meaningful user agent for all HTTP requests
_headers = {"User-Agent": settings.http_client_user_agent}

HttpClient: TypeAlias = "httpx.AsyncClient"
HttpClientSync: TypeAlias = "httpx.Client"


def get_http_client() -> typing.Generator[HttpClient, None, None]:
    yield httpx.AsyncClient(headers=_headers)


def get_http_client_sync() -> typing.Generator[HttpClientSync, None, None]:
    yield httpx.Client(headers=_headers)


def get_base_url(request: Request) -> typing.Generator[str, None, None]:
    if "host" in request.headers:
        host = request.headers["host"]
        proto = "http"
        if "x-forwarded-proto" in request.headers:
            proto = request.headers["x-forwarded-proto"]
        yield f"{proto}://{host}"
    else:
        yield str(request.base_url)


# authentication and authorization
