from datetime import timedelta

from fastapi import FastAPI, HTTPException

from .config import settings
from .db import get_conn, get_cursor
from .schemas import LicenseRequest, DeactivateRequest
from .security import now_utc, hash_license_key, sign_payload

app = FastAPI(title="Fiber License API", version="1.0.0")


def _upsert_trial(cur, app_id: str, machine_id: str):
    cur.execute(
        """
        SELECT id, trial_start, trial_end
        FROM trials
        WHERE app_id=%s AND machine_id=%s
        """,
        (app_id, machine_id),
    )
    row = cur.fetchone()
    now = now_utc()
    if row:
        return row

    trial_end = now + timedelta(days=settings.trial_days)
    cur.execute(
        """
        INSERT INTO trials(app_id, machine_id, trial_start, trial_end, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, trial_start, trial_end
        """,
        (app_id, machine_id, now, trial_end, now, now),
    )
    return cur.fetchone()


def _find_active_license_for_machine(cur, app_id: str, machine_id: str):
    cur.execute(
        """
        SELECT l.id, l.license_key_hash, l.status, l.expires_at
        FROM license_activations a
        JOIN licenses l ON l.id = a.license_id
        WHERE a.app_id=%s AND a.machine_id=%s AND a.status='active' AND l.status='active'
        ORDER BY a.updated_at DESC
        LIMIT 1
        """,
        (app_id, machine_id),
    )
    return cur.fetchone()


def _activation_count(cur, license_id: int):
    cur.execute(
        "SELECT COUNT(*)::int AS c FROM license_activations WHERE license_id=%s AND status='active'",
        (license_id,),
    )
    return int(cur.fetchone()["c"])


def _write_audit(cur, event_type: str, payload: dict):
    now = now_utc()
    cur.execute(
        """
        INSERT INTO audit_logs(event_type, payload_json, created_at)
        VALUES (%s, %s, %s)
        """,
        (event_type, payload, now),
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/trial/start")
def trial_start(req: LicenseRequest):
    with get_conn() as conn, get_cursor(conn) as cur:
        trial = _upsert_trial(cur, req.app_id, req.machine_id)
        _write_audit(cur, "trial_start", req.model_dump())
        return sign_payload(
            {
                "status": "trial",
                "trial_end": trial["trial_end"].isoformat(),
            }
        )


@app.post("/validate")
def validate(req: LicenseRequest):
    with get_conn() as conn, get_cursor(conn) as cur:
        lic = _find_active_license_for_machine(cur, req.app_id, req.machine_id)
        now = now_utc()
        if lic:
            expires = lic["expires_at"]
            if expires is not None and now > expires:
                return sign_payload({"status": "inactive", "message": "License expired."})
            _write_audit(cur, "validate_active", req.model_dump())
            return sign_payload(
                {
                    "status": "active",
                    "license_end": expires.isoformat() if expires else "",
                }
            )

        trial = _upsert_trial(cur, req.app_id, req.machine_id)
        if now <= trial["trial_end"]:
            _write_audit(cur, "validate_trial", req.model_dump())
            return sign_payload({"status": "trial", "trial_end": trial["trial_end"].isoformat()})

        _write_audit(cur, "validate_trial_expired", req.model_dump())
        return sign_payload({"status": "trial_expired", "message": "Trial expired. Activation required."})


@app.post("/activate")
def activate(req: LicenseRequest):
    raw_key = (req.license_key or "").strip()
    if not raw_key:
        raise HTTPException(status_code=400, detail="license_key is required")
    key_hash = hash_license_key(raw_key)

    with get_conn() as conn, get_cursor(conn) as cur:
        cur.execute(
            """
            SELECT id, status, max_devices, expires_at
            FROM licenses
            WHERE app_id=%s AND license_key_hash=%s
            """,
            (req.app_id, key_hash),
        )
        lic = cur.fetchone()
        if not lic:
            _write_audit(cur, "activate_not_found", req.model_dump())
            return sign_payload({"status": "not_found", "message": "Invalid license key."})
        if lic["status"] != "active":
            _write_audit(cur, "activate_blocked", req.model_dump())
            return sign_payload({"status": "inactive", "message": "License is blocked/inactive."})
        if lic["expires_at"] is not None and now_utc() > lic["expires_at"]:
            _write_audit(cur, "activate_expired", req.model_dump())
            return sign_payload({"status": "inactive", "message": "License expired."})

        # Jeśli to samo urządzenie było aktywne wcześniej, odśwież.
        cur.execute(
            """
            SELECT id FROM license_activations
            WHERE app_id=%s AND license_id=%s AND machine_id=%s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (req.app_id, lic["id"], req.machine_id),
        )
        existing = cur.fetchone()
        now = now_utc()
        if not existing:
            cnt = _activation_count(cur, lic["id"])
            if cnt >= int(lic["max_devices"]):
                _write_audit(cur, "activate_limit_reached", req.model_dump())
                return sign_payload({"status": "limit_reached", "message": "Device limit reached."})
            cur.execute(
                """
                INSERT INTO license_activations(app_id, license_id, machine_id, hostname, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'active', %s, %s)
                """,
                (req.app_id, lic["id"], req.machine_id, req.hostname, now, now),
            )
        else:
            cur.execute(
                """
                UPDATE license_activations
                SET status='active', hostname=%s, updated_at=%s
                WHERE id=%s
                """,
                (req.hostname, now, existing["id"]),
            )

        _write_audit(cur, "activate_ok", req.model_dump())
        return sign_payload(
            {
                "status": "active",
                "license_end": lic["expires_at"].isoformat() if lic["expires_at"] else "",
            }
        )


@app.post("/deactivate")
def deactivate(req: DeactivateRequest):
    key_hash = hash_license_key(req.license_key)
    with get_conn() as conn, get_cursor(conn) as cur:
        cur.execute(
            "SELECT id FROM licenses WHERE app_id=%s AND license_key_hash=%s",
            (req.app_id, key_hash),
        )
        lic = cur.fetchone()
        if not lic:
            return sign_payload({"status": "not_found"})

        now = now_utc()
        cur.execute(
            """
            UPDATE license_activations
            SET status='inactive', updated_at=%s
            WHERE app_id=%s AND license_id=%s AND machine_id=%s AND status='active'
            """,
            (now, req.app_id, lic["id"], req.machine_id),
        )
        _write_audit(cur, "deactivate", req.model_dump())
        return sign_payload({"status": "ok"})
