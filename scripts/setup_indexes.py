"""বড় ডেটার জন্য ইনডেক্স তৈরি — বারবার চালালেও নিরাপদ (যা আছে তা আবার বানায় না)।

কখন দরকার:
  - নতুন PostgreSQL ডেটাবেসে `create_all` দিয়ে টেবিল বানানোর পর
  - বা যেকোনো সময় ইনডেক্স মিলিয়ে নিতে

ব্যবহার (প্রজেক্ট ফোল্ডার থেকে):
    python scripts/setup_indexes.py

মনে রাখবেন: এই তালিকা alembic/versions/c4d5e6f7a809_scale_indexes.py এর সাথে মিলিয়ে রাখতে হবে।
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text  # noqa: E402

from app.database import engine  # noqa: E402

SIMPLE_INDEXES = [
    ("ix_people_blood_group", "people", ["blood_group"]),
    ("ix_people_phone", "people", ["phone"]),
    ("ix_families_village", "families", ["village"]),
    ("ix_blood_donors_is_available", "blood_donors", ["is_available"]),
    ("ix_news_is_published", "news", ["is_published"]),
    ("ix_announcements_is_active", "announcements", ["is_active"]),
    ("ix_emergencies_status", "emergencies", ["status"]),
    ("ix_help_requests_status", "help_requests", ["status"]),
]

TRGM_INDEXES = [
    ("ix_people_trgm_first_name", "people", "first_name"),
    ("ix_people_trgm_last_name", "people", "last_name"),
    ("ix_people_trgm_phone", "people", "phone"),
    ("ix_families_trgm_head_name", "families", "head_name"),
    ("ix_families_trgm_family_code", "families", "family_code"),
    ("ix_families_trgm_village", "families", "village"),
]


def main() -> None:
    inspector = inspect(engine)
    created = []

    with engine.begin() as conn:
        for name, table, columns in SIMPLE_INDEXES:
            existing = {ix["name"] for ix in inspector.get_indexes(table)}
            if name not in existing:
                cols = ", ".join(columns)
                conn.execute(text(f"CREATE INDEX {name} ON {table} ({cols})"))
                created.append(name)

        if engine.dialect.name == "postgresql":
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            for name, table, column in TRGM_INDEXES:
                conn.execute(
                    text(f"CREATE INDEX IF NOT EXISTS {name} ON {table} USING gin ({column} gin_trgm_ops)")
                )
                created.append(name)
        else:
            print("নোট: ট্রাইগ্রাম ইনডেক্স শুধু PostgreSQL-এ তৈরি হয় (এখানে স্কিপ)।")

    print("তৈরি হয়েছে:" if created else "সব ইনডেক্স আগে থেকেই আছে।")
    for name in created:
        print("  -", name)


if __name__ == "__main__":
    main()
