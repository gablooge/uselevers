import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uselevers.core.models import Base, MixinCreatedUpdated, id_gen, id_len


class User(Base, MixinCreatedUpdated):
    __tablename__ = "users"  # type: ignore[assignment]
    id: Mapped[str] = mapped_column(
        String(id_len),
        default=id_gen("U"),
        primary_key=True,
    )
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    tokens = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        passive_deletes=True,
        foreign_keys="Token.user_id",
    )


class Token(Base):
    __tablename__ = "tokens"  # type: ignore[assignment]
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    access_token = Column(String(450), primary_key=True)
    refresh_token = Column(String(450), nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now)
    expired_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tokens", foreign_keys=[user_id])
