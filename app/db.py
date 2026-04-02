from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings


@contextmanager
def get_conn():
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured.")
    conn = psycopg2.connect(settings.database_url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor(conn):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
    finally:
        cur.close()
