"""add division, district, upazila, village, para, photo_url to users

Revision ID: e6a7b8c9d012
Revises: d5f6a7b8c901
Create Date: 2026-10-12 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e6a7b8c9d012'
down_revision: Union[str, Sequence[str], None] = 'd5f6a7b8c901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('division', sa.String(length=50), nullable=True))
        batch.add_column(sa.Column('district', sa.String(length=50), nullable=True))
        batch.add_column(sa.Column('upazila', sa.String(length=50), nullable=True))
        batch.add_column(sa.Column('village', sa.String(length=50), nullable=True))
        batch.add_column(sa.Column('para', sa.String(length=50), nullable=True))
        batch.add_column(sa.Column('photo_url', sa.String(length=255), nullable=True))
        batch.create_index('ix_users_village', ['village'], unique=False)
        batch.create_index('ix_users_para', ['para'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.drop_index('ix_users_para')
        batch.drop_index('ix_users_village')
        batch.drop_column('photo_url')
        batch.drop_column('para')
        batch.drop_column('village')
        batch.drop_column('upazila')
        batch.drop_column('district')
        batch.drop_column('division')