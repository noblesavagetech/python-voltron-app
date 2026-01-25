#!/usr/bin/env python3
"""
Idempotent migration script to switch MFA from Vonage SMS to TOTP.

What it does:
- Adds `mfa_secret` column to `users` (if it doesn't exist)
- Drops `phone` column (if it exists)
- Drops `vonage_request_id` column (if it exists)

How to run:
1) Set DATABASE_URL env var to your Railway Postgres connection string, e.g.
   postgresql://postgres:<PASSWORD>@<HOST>:<PORT>/<DBNAME>

2) Run:
   python scripts/migrate_totp.py

Requirements:
- psycopg2-binary is already in requirements.txt

Safe to run multiple times.
"""
import os
import sys
import urllib.parse
import psycopg2

SQL_STATEMENTS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_secret VARCHAR(32);",
    "ALTER TABLE users DROP COLUMN IF EXISTS phone;",
    "ALTER TABLE users DROP COLUMN IF EXISTS vonage_request_id;",
]


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL is not set. You can export it or pass it as the first argument.")
        if len(sys.argv) > 1:
            db_url = sys.argv[1]
        else:
            print("Usage: DATABASE_URL=postgresql://user:pass@host:port/db python scripts/migrate_totp.py")
            sys.exit(1)

    # Ensure postgresql:// prefix
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        # psycopg2 can accept the URL directly
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        cur = conn.cursor()

        print("🚧 Applying TOTP migration...")
        for sql in SQL_STATEMENTS:
            print(f"   → {sql}")
            cur.execute(sql)

        conn.commit()
        cur.close()
        conn.close()
        print("\n✅ Migration complete. TOTP MFA is ready to use.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
