import argparse
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

import psycopg2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--app-id", default="fiber_invoiceflow")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--max-devices", type=int, default=1)
    args = parser.parse_args()

    raw_key = "FIBER-" + secrets.token_urlsafe(24).upper().replace("-", "")[:32]
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    exp = datetime.now(timezone.utc) + timedelta(days=args.days)

    conn = psycopg2.connect(args.database_url)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO licenses(app_id, license_key_hash, status, max_devices, expires_at)
        VALUES (%s, %s, 'active', %s, %s)
        """,
        (args.app_id, key_hash, args.max_devices, exp),
    )
    conn.commit()
    cur.close()
    conn.close()

    print("RAW_LICENSE_KEY=", raw_key)
    print("EXPIRES_AT=", exp.isoformat())


if __name__ == "__main__":
    main()
