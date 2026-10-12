"""add image_url to mosques, institutions, news

Revision ID: a1b2c3d4e567
Revises: f7b8c9d0e123
Create Date: 2026-10-12 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e567'
down_revision: Union[str, Sequence[str], None] = 'f7b8c9d0e123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = ('mosques', 'institutions', 'news')


def upgrade() -> None:
    for table in TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column('image_url', sa.String(length=255), nullable=True))


def downgrade() -> None:
    for table in TABLES:
        with op.batch_alter_table(table) as batch:
            batch.drop_column('image_url')