from collections.abc import Generator
from urllib.parse import ParseResult, urlparse

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from uselevers.core import deps
from uselevers.core.config import settings
from uselevers.core.db import engine_options, session_options
from uselevers.main import app
from uselevers.tests.utils import random_lower_string


def random_database_uri(original: str) -> ParseResult:
    database = "test-" + random_lower_string(32)
    url = urlparse(original)
    return url._replace(path=database)


@pytest.fixture(scope="session")
def alembic_engine() -> Generator[Engine, None, None]:
    # Configure a random database URI
    sqlalchemy_new_uri = random_database_uri(str(settings.SQLALCHEMY_DATABASE_URI))
    sqlalchemy_database = sqlalchemy_new_uri.path.replace("/", "")

    # Create an engine to connect to the default URL
    setup_engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        **engine_options,
        isolation_level="AUTOCOMMIT",
    )
    # Create the database
    with setup_engine.begin() as conn:
        conn.execute(text(f'CREATE DATABASE "{sqlalchemy_database}"'))

    yield setup_engine
    setup_engine.dispose()

    # Delete the database
    with setup_engine.begin() as conn:
        conn.execute(text(f'DROP DATABASE "{sqlalchemy_database}"'))


@pytest.fixture(scope="function")
def SessionTest(alembic_engine: Engine) -> Generator[sessionmaker[Session], None, None]:
    # Configure Alembic
    config = Config(settings.DEV_MIGRATIONS_ALEMBIC_INI)
    config.set_main_option("sqlalchemy.url", str(alembic_engine.url))

    upgrade(config, "head")

    SessionTest = sessionmaker(  # type: ignore[call-overload]
        bind=alembic_engine,
        **session_options,
    )
    yield SessionTest

    downgrade(config, "base")


@pytest.fixture()
def client(SessionTest: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    def get_db() -> Generator[Session, None, None]:
        with SessionTest() as session:
            yield session

    app.dependency_overrides[deps.get_db] = get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db(SessionTest: sessionmaker[Session]) -> Generator[Session, None, None]:
    with SessionTest() as session:
        yield session
