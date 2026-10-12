"""add full_name, make email optional

Revision ID: d5f6a7b8c901
Revises: c4d5e6f7a809
Create Date: 2026-10-12 10:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd5f6a7b8c901'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a809'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('full_name', sa.String(length=150), nullable=True))
        batch.alter_column(
            'email',
            existing_type=sa.String(length=120),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.alter_column(
            'email',
            existing_type=sa.String(length=120),
            nullable=False,
        )
        batch.drop_column('full_name')