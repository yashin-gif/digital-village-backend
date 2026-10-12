import sys

from sqlalchemy import text

from app.database import engine

username = sys.argv[1]

with engine.begin() as conn:
    result = conn.execute(text("DELETE FROM users WHERE username = :u"), {"u": username})
    print(f"মুছে ফেলা হয়েছে: {result.rowcount} টি")
