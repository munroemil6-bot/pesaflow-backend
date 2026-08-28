# PesaFlow Backend

PesaFlow is a Django REST Framework backend for a money-transfer application. It provides authentication, wallets, beneficiaries, transfers, administrator reporting, and M-PESA Daraja integration.

## Live Deployment

- Backend API: https://pesaflow-backend-wdbv.onrender.com
- API root: https://pesaflow-backend-wdbv.onrender.com/api/
- Django admin: https://pesaflow-backend-wdbv.onrender.com/admin/
- Frontend: deployed separately with Vercel

The API root returns the service status and available API areas:

```json
{
  "status": "ok",
  "service": "pesaflow-backend",
  "api_types": [
    "accounts",
    "wallet",
    "beneficiaries",
    "transactions",
    "payments",
    "admin-dashboard"
  ]
}
```

## Technology

- Python 3.14-compatible Django 5.2
- Django REST Framework and Simple JWT
- PostgreSQL on Render; SQLite for local development
- M-PESA Daraja API
- Gunicorn and WhiteNoise

## Local Setup

Run from the backend directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/api/ or http://127.0.0.1:8000/admin/.

```bash
deactivate
```

## Environment Variables

Use `.env.example` for local configuration. Never commit passwords, database credentials, JWT secrets, or Daraja secrets.

```text
DATABASE_URL=
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:8000

MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=
```

## API Endpoints

All paths below are relative to `https://pesaflow-backend-wdbv.onrender.com/api/`.

### Accounts

```text
GET  /accounts/
POST /accounts/register/
POST /accounts/login/
POST /accounts/refresh/
GET  /accounts/profile/
PUT  /accounts/profile/
POST /accounts/logout/
POST /accounts/change-password/
```

### Wallet

```text
GET  /wallet/
GET  /wallet/balance/
GET  /wallet/analytics/
GET  /wallet/history/
POST /wallet/add-funds/
```

### Beneficiaries

```text
GET    /beneficiaries/
POST   /beneficiaries/
GET    /beneficiaries/<id>/
PUT    /beneficiaries/<id>/
DELETE /beneficiaries/<id>/
```

### Transactions

```text
GET  /transactions/
GET  /transactions/summary/
GET  /transactions/sent/
GET  /transactions/received/
GET  /transactions/<id>/
```

### Payments

```text
POST /payments/stk-push/
```

The STK push endpoint requires authentication and Daraja sandbox credentials. The callback, payment-status, simulation, and access-token routes are not currently exposed by `payments/urls.py`.

### Admin Dashboard

These endpoints require an authenticated administrator:

```text
GET /admin-dashboard/summary/
GET /admin-dashboard/users/
GET /admin-dashboard/users/<id>/
GET /admin-dashboard/transactions/
GET /admin-dashboard/wallets/
GET /admin-dashboard/analytics/
GET /admin-dashboard/revenue/
GET /admin-dashboard/top-users/
GET /admin-dashboard/payment-status/
```

## Authentication

Login with an email or phone number:

```http
POST /api/accounts/login/
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

The response contains `access`, `refresh`, and `user`. Send the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

Use the refresh token only with `POST /api/accounts/refresh/`. Access tokens expire after one hour; refresh tokens expire after seven days.

## Vercel Frontend

For a Vite frontend, add this Vercel environment variable:

```text
VITE_API_URL=https://pesaflow-backend-wdbv.onrender.com/api
```

For Next.js, use:

```text
NEXT_PUBLIC_API_URL=https://pesaflow-backend-wdbv.onrender.com/api
```

After changing Vercel variables, redeploy the frontend. Render must include the deployed frontend URL in both `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`.

## Render Deployment

The repository includes `render.yaml` with these commands:

```bash
pip install -r requirements.txt && python manage.py collectstatic --no-input
python manage.py migrate && python manage.py ensure_admin && python manage.py seed_demo_data && gunicorn pesaflow.wsgi:application
```

Render must define `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, the `ADMIN_*` variables, and the `MPESA_*` variables. Daraja credentials must be entered as Render secret environment variables and never committed. Register this callback URL in Daraja:

```text
https://pesaflow-backend-wdbv.onrender.com/api/payments/callback/
```

Callback processing is not yet implemented in the current payments app.

## Demo Data

Render runs `seed_demo_data` after migrations. It creates or updates seven demo users, wallets, beneficiaries, transfers, one dashboard snapshot, and one dashboard log. It is repeatable and does not create duplicates.

Run locally with:

```bash
python manage.py seed_demo_data
```

Demo passwords use the development-only pattern `firstname1234`, such as `amina1234`. Change or remove demo accounts before using real users.

## Testing

```bash
python manage.py check
python manage.py test
```

External Daraja calls should be mocked in tests.
