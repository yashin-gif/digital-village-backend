"""scale: indexes for large tables and trigram search on PostgreSQL

Revision ID: c4d5e6f7a809
Revises: b3e8f1a2c906
Create Date: 2026-10-11 02:00:00

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c4d5e6f7a809'
down_revision: Union[str, Sequence[str], None] = 'b3e8f1a2c906'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# সাধারণ B-tree ইনডেক্স: ফিল্টারে দ্রুত আনে (SQLite ও PostgreSQL দুটোতেই)
SIMPLE_INDEXES = [
    ('ix_people_blood_group', 'people', ['blood_group']),
    ('ix_people_phone', 'people', ['phone']),
    ('ix_families_village', 'families', ['village']),
    ('ix_blood_donors_is_available', 'blood_donors', ['is_available']),
    ('ix_news_is_published', 'news', ['is_published']),
    ('ix_announcements_is_active', 'announcements', ['is_active']),
    ('ix_emergencies_status', 'emergencies', ['status']),
    ('ix_help_requests_status', 'help_requests', ['status']),
]

# PostgreSQL ট্রাইগ্রাম ইনডেক্স: '%খোঁজ%' (ILIKE) লাখো সারিতেও দ্রুত করে
TRGM_INDEXES = [
    ('ix_people_trgm_first_name', 'people', 'first_name'),
    ('ix_people_trgm_last_name', 'people', 'last_name'),
    ('ix_people_trgm_phone', 'people', 'phone'),
    ('ix_families_trgm_head_name', 'families', 'head_name'),
    ('ix_families_trgm_family_code', 'families', 'family_code'),
    ('ix_families_trgm_village', 'families', 'village'),
]


def upgrade() -> None:
    for name, table, columns in SIMPLE_INDEXES:
        op.create_index(name, table, columns, unique=False)

    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
        for name, table, column in TRGM_INDEXES:
            op.execute(
                f'CREATE INDEX IF NOT EXISTS {name} ON {table} USING gin ({column} gin_trgm_ops)'
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        for name, _table, _column in TRGM_INDEXES:
            op.execute(f'DROP INDEX IF EXISTS {name}')

    for name, table, _columns in SIMPLE_INDEXES:
        op.drop_index(name, table_name=table)
