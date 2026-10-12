"""Neon/PostgreSQL ডেটাবেসের public স্কিমা মুছে নতুন করে বানায়।

সতর্কতা: এটা ডেটাবেসের সব টেবিল ও ডেটা মুছে দেয়।
শুধু নতুন বা পরীক্ষার ডেটাবেসের জন্য ব্যবহার করুন।
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import text  # noqa: E402

from app.database import engine  # noqa: E402

print("ডেটাবেসের public স্কিমা মুছে নতুন করে বানানো হচ্ছে...")

with engine.begin() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))

print("সম্পন্ন। এখন alembic upgrade head চালান।")
