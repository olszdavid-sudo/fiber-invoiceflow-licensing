# Fiber License Backend (FastAPI)

Backend do trial/licencji dla aplikacji desktop.

## 1) Supabase SQL

Wklej zawartość `sql/schema.sql` do SQL Editor i uruchom.

## 2) Render deploy

1. Podłącz repo do Render.
2. Ustaw `Root Directory` na `backend`.
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Dodaj env:
   - `DATABASE_URL`
   - `LICENSE_SIGNING_SECRET`
   - `LICENSE_TRIAL_DAYS=30`

## 3) Endpointy

- `POST /trial/start`
- `POST /validate`
- `POST /activate`
- `POST /deactivate`
- `GET /health`

Wszystkie endpointy przyjmują JSON opisany w `app/schemas.py`.

## 4) Klient desktop

W aplikacji desktop ustaw:

`FIBER_LICENSE_API_URL=https://<twoj-render-url>`

Opcjonalnie podpis:

`FIBER_LICENSE_SIGNING_SECRET=<ten-sam-jak-backend>`
