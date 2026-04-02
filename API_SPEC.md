# API Spec v1

## POST /validate

Request:

```json
{
  "app_id": "fiber_invoiceflow",
  "app_version": "1.6.x",
  "machine_id": "<sha256-device-id>",
  "hostname": "DESKTOP-123",
  "license_key": "opcjonalnie-z-cache"
}
```

Response:

- `status=trial` + `trial_end`
- `status=active` + `license_end`
- `status=trial_expired|inactive|not_found|needs_activation`

## POST /activate

Jak `validate`, ale `license_key` wymagany.

## POST /deactivate

Request:

```json
{
  "app_id": "fiber_invoiceflow",
  "machine_id": "<sha256-device-id>",
  "license_key": "FIBER-XXXX"
}
```

## POST /trial/start

Tworzy trial, jeżeli jeszcze nie istnieje.
