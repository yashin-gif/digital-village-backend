"""add birth_year to users

Revision ID: f7b8c9d0e123
Revises: e6a7b8c9d012
Create Date: 2026-10-12 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f7b8c9d0e123'
down_revision: Union[str, Sequence[str], None] = 'e6a7b8c9d012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('birth_year', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.drop_column('birth_year')