import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone

from .config import settings


def now_utc():
    return datetime.now(timezone.utc)


def hash_license_key(raw_key: str) -> str:
    return hashlib.sha256((raw_key or "").strip().encode("utf-8")).hexdigest()


def sign_payload(payload: dict) -> dict:
    body = dict(payload or {})
    if not settings.signing_secret:
        return body
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hmac.new(
        settings.signing_secret.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    body["signature"] = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return body
