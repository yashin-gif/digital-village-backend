"""প্রথম অ্যাডমিন তৈরি বা বিদ্যমান ইউজারকে অ্যাডমিন বানানো।

ব্যবহার (প্রজেক্ট ফোল্ডার থেকে):
    python scripts/create_admin.py --username karim --email karim@example.com --phone 01700000000
পাসওয়ার্ড দিতে না চাইলে প্রম্পটে জিজ্ঞেস করবে।
"""

import argparse
import getpass
import os
import sys

# প্রজেক্টের root (app ফোল্ডার) যেন import হয়
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.security import hash_password  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import User  # noqa: E402
from app.services.audit_service import log_action  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--phone", required=True)
    parser.add_argument("--password", help="না দিলে প্রম্পটে জিজ্ঞেস করবে")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")
    if len(password) < 6:
        raise SystemExit("Password must be at least 6 characters")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter((User.username == args.username) | (User.email == args.email))
            .first()
        )

        if user:
            user.role = "admin"
            user.is_active = True
            action = "promoted to admin"
        else:
            user = User(
                username=args.username,
                email=args.email,
                phone=args.phone,
                password_hash=hash_password(password),
                role="admin",
                is_active=True,
            )
            db.add(user)
            action = "created as admin"

        db.commit()
        db.refresh(user)
        log_action(db, user.id, "user.bootstrap_admin", "users", user.id)

        print(f"OK: {user.username} {action}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
