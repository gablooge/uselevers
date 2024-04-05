from collections.abc import Callable
from datetime import datetime

from shortuuid import ShortUUID
from sqlalchemy import DateTime, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

shortuuid = ShortUUID(alphabet="0123456789abcdefghijklmnopqrstuvwxyz")

# Documentation: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html


class Base(DeclarativeBase):
    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls) -> str:
        """
        Overwrite tablename

        :return: Tablename in lowercase
        """
        return cls.__name__.lower()


class MixinCreatedUpdated:
    updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=text("NOW()::timestamp"),
        onupdate=func.now(),
    )
    created: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=text("NOW()::timestamp"),
    )


def id_gen(prefix: str) -> Callable[[], str]:
    return lambda: prefix + shortuuid.uuid()


id_len = shortuuid.encoded_length() + 7
id_regex = r"^[0-9a-z-]+$"
