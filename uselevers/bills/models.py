from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from uselevers.core.models import Base, MixinCreatedUpdated, id_gen, id_len


class Bill(Base, MixinCreatedUpdated):
    __tablename__ = "bills"  # type: ignore[assignment]
    id: Mapped[str] = mapped_column(
        String(id_len),
        default=id_gen("B"),
        primary_key=True,
    )
    total = mapped_column(Float, nullable=False)

    sub_bills = relationship(
        "SubBill",
        back_populates="bill",
        cascade="all, delete-orphan",
        lazy="dynamic",
        passive_deletes=True,
        foreign_keys="SubBill.bill_id",
    )

    # Add a CheckConstraint to enforce that total must be positive
    __table_args__ = (CheckConstraint("total >= 0", name="check_positive_total"),)


class SubBill(Base, MixinCreatedUpdated):
    __tablename__ = "sub_bills"  # type: ignore[assignment]
    id: Mapped[str] = mapped_column(
        String(id_len),
        default=id_gen("SB"),
        primary_key=True,
    )
    bill_id = Column(String, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    amount = mapped_column(Float, nullable=False)
    reference = Column(String, nullable=True)

    bill = relationship("Bill", back_populates="sub_bills", foreign_keys=[bill_id])

    __table_args__ = (
        Index("unique_reference_case_insensitive", func.lower(reference), unique=True),
    )
