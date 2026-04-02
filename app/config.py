import os


class Settings:
    database_url = os.environ.get("DATABASE_URL", "").strip()
    app_secret = os.environ.get("LICENSE_APP_SECRET", "").strip()
    signing_secret = os.environ.get("LICENSE_SIGNING_SECRET", "").strip()
    admin_api_key = os.environ.get("ADMIN_API_KEY", "").strip()
    trial_days = int(os.environ.get("LICENSE_TRIAL_DAYS", "30"))
    max_clock_skew_sec = int(os.environ.get("LICENSE_MAX_CLOCK_SKEW_SEC", "300"))


settings = Settings()
