"""add user role column for auth

Revision ID: 20260512_0002
Revises: 20260201_0001
Create Date: 2026-05-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260512_0002"
down_revision: Union[str, None] = "20260201_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=32), nullable=True))
    op.execute("UPDATE users SET role = 'customer' WHERE role IS NULL")
    op.alter_column("users", "role", nullable=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
