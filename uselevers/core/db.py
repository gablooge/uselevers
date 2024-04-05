from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

engine_options = {
    "pool_pre_ping": True,
}

session_options = {
    "autoflush": False,
    "autocommit": False,
    "autobegin": False,
}

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), **engine_options)
SessionLocal = sessionmaker(  # type: ignore[call-overload]
    bind=engine,
    **session_options,
)
