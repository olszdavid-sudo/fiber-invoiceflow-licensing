from datetime import timedelta
import secrets

from fastapi import FastAPI, HTTPException
from psycopg2.extras import Json
from fastapi.responses import HTMLResponse

from .config import settings
from .db import get_conn, get_cursor
from .schemas import LicenseRequest, DeactivateRequest, AdminGenerateRequest
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
        (event_type, Json(payload or {}), now),
    )


def _generate_raw_license_key() -> str:
    # 16 bytes -> 32 hex chars, format zgodny z dotychczasowymi kluczami.
    return "FIBER-" + secrets.token_hex(16).upper()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return """
<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fiber License Admin</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f6f7fb; margin:0; }
    .wrap { max-width: 760px; margin: 36px auto; background:#fff; border:1px solid #d8deea; border-radius:14px; padding:22px; }
    h2 { margin:0 0 14px; }
    label { display:block; margin:10px 0 6px; font-weight:600; }
    input { width:100%; padding:10px; border:1px solid #c8d0dd; border-radius:8px; }
    button { margin-top:14px; padding:10px 14px; border:0; border-radius:8px; background:#0b5fff; color:#fff; font-weight:700; cursor:pointer; }
    pre { margin-top:14px; padding:12px; background:#0b1324; color:#d6e6ff; border-radius:8px; min-height:80px; overflow:auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>Fiber - Panel Licencji</h2>
    <label>ADMIN_API_KEY</label>
    <input id="admin_api_key" type="password" placeholder="Wpisz klucz admina" />
    <label>app_id</label>
    <input id="app_id" value="fiber_invoiceflow" />
    <label>max_devices</label>
    <input id="max_devices" type="number" value="1" min="1" max="100" />
    <label>validity_days</label>
    <input id="validity_days" type="number" value="365" min="1" />
    <button id="gen">Wygeneruj klucz</button>
    <pre id="out">Gotowe.</pre>
  </div>
  <script>
    document.getElementById("gen").addEventListener("click", async () => {
      const payload = {
        admin_api_key: document.getElementById("admin_api_key").value.trim(),
        app_id: document.getElementById("app_id").value.trim(),
        max_devices: Number(document.getElementById("max_devices").value || 1),
        validity_days: Number(document.getElementById("validity_days").value || 365),
      };
      const out = document.getElementById("out");
      out.textContent = "Generowanie...";
      try {
        const res = await fetch("/admin/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        out.textContent = "Blad: " + String(e);
      }
    });
  </script>
</body>
</html>
"""


@app.post("/admin/generate")
def admin_generate(req: AdminGenerateRequest):
    if not settings.admin_api_key:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY is not configured on server.")
    if req.admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key.")

    raw_key = _generate_raw_license_key()
    key_hash = hash_license_key(raw_key)
    now = now_utc()
    expires = now + timedelta(days=int(req.validity_days))

    with get_conn() as conn, get_cursor(conn) as cur:
        cur.execute(
            """
            INSERT INTO licenses(app_id, license_key_hash, status, max_devices, expires_at, created_at, updated_at)
            VALUES (%s, %s, 'active', %s, %s, %s, %s)
            ON CONFLICT (app_id, license_key_hash)
            DO UPDATE SET
              status='active',
              max_devices=EXCLUDED.max_devices,
              expires_at=EXCLUDED.expires_at,
              updated_at=EXCLUDED.updated_at
            RETURNING id, expires_at
            """,
            (req.app_id, key_hash, int(req.max_devices), expires, now, now),
        )
        row = cur.fetchone()
        _write_audit(
            cur,
            "admin_generate_license",
            {
                "app_id": req.app_id,
                "max_devices": req.max_devices,
                "validity_days": req.validity_days,
                "license_id": int(row["id"]),
            },
        )

    return sign_payload(
        {
            "status": "ok",
            "license_key": raw_key,
            "app_id": req.app_id,
            "max_devices": int(req.max_devices),
            "expires_at": row["expires_at"].isoformat() if row and row.get("expires_at") else "",
        }
    )


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
