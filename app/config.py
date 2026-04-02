import os


def _env_bool(name: str, default: bool) -> bool:
    raw = str(os.environ.get(name, "") or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "y", "on"}


class Settings:
    database_url = os.environ.get("DATABASE_URL", "").strip()
    app_secret = os.environ.get("LICENSE_APP_SECRET", "").strip()
    signing_secret = os.environ.get("LICENSE_SIGNING_SECRET", "").strip()
    admin_api_key = os.environ.get("ADMIN_API_KEY", "").strip()
    # Gdy True: brak trial bez kodu, wymagaj klucza od pierwszego uruchomienia.
    require_key_on_first_run = _env_bool("LICENSE_REQUIRE_KEY_ON_FIRST_RUN", True)
    # Globalny limit aktywnych urządzeń/osób na aplikację.
    max_active_machines_per_app = int(os.environ.get("LICENSE_MAX_ACTIVE_MACHINES_PER_APP", "2"))
    trial_days = int(os.environ.get("LICENSE_TRIAL_DAYS", "30"))
    max_clock_skew_sec = int(os.environ.get("LICENSE_MAX_CLOCK_SKEW_SEC", "300"))


settings = Settings()
