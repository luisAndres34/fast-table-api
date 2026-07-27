"""add paid to orderstatus enum

Revision ID: f1e2d3c4b5a6
Revises: cb0d7e6637ed
Create Date: 2026-07-27 19:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, Sequence[str], None] = 'cb0d7e6637ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Execute native PostgreSQL command to append 'paid' to the DB Enum type
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'paid'")

def downgrade() -> None:
    pass
