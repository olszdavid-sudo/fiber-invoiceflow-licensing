CREATE TABLE IF NOT EXISTS licenses (
    id BIGSERIAL PRIMARY KEY,
    app_id TEXT NOT NULL,
    license_key_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    max_devices INT NOT NULL DEFAULT 1,
    expires_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(app_id, license_key_hash)
);

CREATE TABLE IF NOT EXISTS license_activations (
    id BIGSERIAL PRIMARY KEY,
    app_id TEXT NOT NULL,
    license_id BIGINT NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    machine_id TEXT NOT NULL,
    hostname TEXT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(app_id, license_id, machine_id)
);

CREATE INDEX IF NOT EXISTS idx_license_activations_machine
ON license_activations(app_id, machine_id, status);

CREATE TABLE IF NOT EXISTS trials (
    id BIGSERIAL PRIMARY KEY,
    app_id TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    trial_start TIMESTAMPTZ NOT NULL,
    trial_end TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(app_id, machine_id)
);

CREATE INDEX IF NOT EXISTS idx_trials_machine ON trials(app_id, machine_id);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
