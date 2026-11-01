"""
Ye script confirm karega:
1. Kaunsa DATABASE_URL actually use ho raha hai
2. motherboard table ka LIVE schema (jo is connection se dikh raha hai)

Chalane ka tareeka:
    python check_db.py
"""

import os
from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL", "sqlite:///rigbuilder.db")

print("=" * 60)
print("CURRENTLY USING DATABASE_URL:")
# Password ko chhupa ke dikhate hain (security ke liye)
if "@" in db_url:
    masked = db_url.split("@")[0].split(":")[0] + ":****@" + db_url.split("@")[1]
    print(masked)
else:
    print(db_url)
print("=" * 60)

engine = create_engine(db_url)

with engine.connect() as conn:
    # Confirm karo konsa database/project hai
    result = conn.execute(text("SELECT current_database();"))
    print("\nConnected to database:", result.fetchone()[0])

    # motherboard table ka live schema check karo
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'motherboard'
        ORDER BY ordinal_position;
    """))
    print("\nLIVE Schema for 'motherboard' table (as seen by this connection):")
    print("-" * 60)
    for row in result:
        print(f"{row[0]:30} {row[1]}")
    print("-" * 60)
