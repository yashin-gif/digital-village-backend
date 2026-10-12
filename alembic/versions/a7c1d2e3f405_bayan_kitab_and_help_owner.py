"""bayan, kitab and help request owner

Revision ID: a7c1d2e3f405
Revises: bfc87f0d8770
Create Date: 2026-10-11 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7c1d2e3f405'
down_revision: Union[str, Sequence[str], None] = 'bfc87f0d8770'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'bayan_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mosque_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('speaker_name', sa.String(length=150), nullable=True),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['mosque_id'], ['mosques.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_bayan_sessions_id'), 'bayan_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_bayan_sessions_mosque_id'), 'bayan_sessions', ['mosque_id'], unique=False)
    op.create_index(op.f('ix_bayan_sessions_session_date'), 'bayan_sessions', ['session_date'], unique=False)

    op.create_table(
        'kitabs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('author', sa.String(length=150), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_kitabs_id'), 'kitabs', ['id'], unique=False)

    op.create_table(
        'kitab_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kitab_id', sa.Integer(), nullable=False),
        sa.Column('read_date', sa.Date(), nullable=False),
        sa.Column('from_reference', sa.String(length=100), nullable=True),
        sa.Column('to_reference', sa.String(length=100), nullable=True),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['kitab_id'], ['kitabs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_kitab_progress_id'), 'kitab_progress', ['id'], unique=False)
    op.create_index(op.f('ix_kitab_progress_kitab_id'), 'kitab_progress', ['kitab_id'], unique=False)
    op.create_index(op.f('ix_kitab_progress_read_date'), 'kitab_progress', ['read_date'], unique=False)

    with op.batch_alter_table('help_requests') as batch:
        batch.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch.create_index('ix_help_requests_user_id', ['user_id'], unique=False)
        batch.create_foreign_key(
            'fk_help_requests_user_id_users', 'users', ['user_id'], ['id'], ondelete='SET NULL'
        )


def downgrade() -> None:
    with op.batch_alter_table('help_requests') as batch:
        batch.drop_constraint('fk_help_requests_user_id_users', type_='foreignkey')
        batch.drop_index('ix_help_requests_user_id')
        batch.drop_column('user_id')

    op.drop_index(op.f('ix_kitab_progress_read_date'), table_name='kitab_progress')
    op.drop_index(op.f('ix_kitab_progress_kitab_id'), table_name='kitab_progress')
    op.drop_index(op.f('ix_kitab_progress_id'), table_name='kitab_progress')
    op.drop_table('kitab_progress')

    op.drop_index(op.f('ix_kitabs_id'), table_name='kitabs')
    op.drop_table('kitabs')

    op.drop_index(op.f('ix_bayan_sessions_session_date'), table_name='bayan_sessions')
    op.drop_index(op.f('ix_bayan_sessions_mosque_id'), table_name='bayan_sessions')
    op.drop_index(op.f('ix_bayan_sessions_id'), table_name='bayan_sessions')
    op.drop_table('bayan_sessions')
