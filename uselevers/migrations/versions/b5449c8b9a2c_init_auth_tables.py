"""
init auth tables

Revision ID: b5449c8b9a2c
Revises:
Create Date: 2024-04-05 23:00:02.591077

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b5449c8b9a2c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "tokens",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(length=450), nullable=False),
        sa.Column("refresh_token", sa.String(length=450), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expired_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("access_token"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tokens")
    op.drop_table("users")
    # ### end Alembic commands ###