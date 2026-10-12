"""add token_version to users

Revision ID: b3e8f1a2c906
Revises: a7c1d2e3f405
Create Date: 2026-10-11 01:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3e8f1a2c906'
down_revision: Union[str, Sequence[str], None] = 'a7c1d2e3f405'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.add_column(
            sa.Column('token_version', sa.Integer(), nullable=False, server_default='0')
        )


def downgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.drop_column('token_version')
