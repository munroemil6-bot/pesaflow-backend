# PesaFlow Backend

PesaFlow is a Flask REST API for the PesaFlow React money-transfer frontend.
The backend will replace the frontend's current browser `localStorage` mock
database with secure authentication, PostgreSQL persistence, wallets,
beneficiaries, transfers, M-PESA funding, and administrator reporting.

## Technology

- Python 3.12 and Pipenv
- Flask and Flask-SQLAlchemy
- Flask-Migrate for database migrations
- Flask-JWT-Extended for JWT authentication
- Flask-CORS for frontend access
- Marshmallow for JSON validation and serialization
- PostgreSQL through `psycopg2-binary`
- Requests for Safaricom Daraja API calls
- Pytest for automated tests

## Structure

```text
pesaflow-backend/
├── app/
│   ├── __init__.py       # Myles: extensions and application factory
│   ├── models.py         # SQLAlchemy models and relationships
│   ├── schemas.py        # JSON request validation and responses
│   ├── routes.py         # Direct @app REST routes
│   └── services.py       # Business logic and Daraja communication
├── migrations/           # Database migration revisions
├── tests/                # Auth, wallet, transaction, and M-PESA tests
├── config.py             # Environment-backed configuration
├── run.py                # Local development entry point
├── .env.example          # Safe configuration template
├── Pipfile
└── Pipfile.lock
```

## Setup

Run these commands from the backend directory:

```bash
pipenv --python 3.12
pipenv install
pipenv install --dev pytest
cp .env.example .env
pipenv run python run.py
```

The API runs at `http://127.0.0.1:5000`.

Verify the current application foundation:

```bash
curl http://127.0.0.1:5000/api/health
```

Expected response:

```json
{ "service": "pesaflow-backend", "status": "ok" }
```

## Environment and Security

Add local values to `.env`. Never commit `.env`, passwords, M-PESA consumer
secrets, passkeys, database passwords, or JWT secrets. M-PESA credentials must
remain on the server and must never be placed in the React application.

Required variables:

```text
DATABASE_URL=
JWT_SECRET_KEY=
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=
MPESA_ENVIRONMENT=sandbox
```

## API Style

This project uses a REST API over HTTP. Requests and responses use JSON.
Routes are registered directly on the Flask application inside
`register_routes(app)` in `app/routes.py`. Do not use Flask blueprints.

Example route style:

```python
@app.post("/api/example")
def example():
		...
```

Protected endpoints require:

```text
Authorization: Bearer <jwt-access-token>
```

Use these status codes:

- `200`: successful read or update
- `201`: successful creation
- `204`: successful deletion with no response body
- `400`: invalid input
- `401`: missing or invalid JWT
- `403`: authenticated but not authorized
- `404`: record not found or not visible
- `409`: duplicate or conflicting data

Routes should authenticate, validate, call a service, and return JSON. Business
rules and database changes belong in `app/services.py`, not in route handlers.

## Models and Relationships

### User

Fields include `id`, `full_name`, `email`, `phone`, `password_hash`, `role`,
account status, and timestamps.

- One User has one Wallet.
- One User has many Beneficiaries.
- One User sends many Transactions.
- One User receives many Transactions.

### Wallet

Fields include `user_id`, `balance`, `currency`, and timestamps. `user_id` is a
unique foreign key to `User.id`.

### Beneficiary

Fields include `user_id`, `name`, `phone`, and `created_at`. Each beneficiary
belongs to one User and must only be visible to that owner.

### Transaction

Fields include `sender_id`, `recipient_id`, `amount`, `fee`, `total_amount`,
`status`, `reference`, `description`, `transaction_type`, and `created_at`.
Both sender and recipient IDs reference `User.id`.

### MpesaTransaction

Fields include `transaction_id`, `phone_number`, `amount`, Daraja request IDs,
receipt number, result code, result description, status, and timestamps. Each
M-PESA record belongs to one Transaction.

Use fixed-precision numeric types for money. Add foreign keys, indexes,
constraints, and migration support.

## API Contract and Ownership

### Mason: Authentication and Profile

| Method | Endpoint             | Responsibility                                       |
| ------ | -------------------- | ---------------------------------------------------- |
| POST   | `/api/auth/register` | Validate data, hash password, create User and Wallet |
| POST   | `/api/auth/login`    | Verify password and return JWT                       |
| GET    | `/api/auth/me`       | Return authenticated User                            |
| GET    | `/api/users/me`      | Return authenticated profile                         |
| PUT    | `/api/users/me`      | Update allowed profile fields                        |

Registration accepts `full_name`, `email`, `phone`, and `password`. Passwords
must be hashed and never returned.

### Naomi: Wallet and Beneficiaries

| Method | Endpoint                  | Responsibility                   |
| ------ | ------------------------- | -------------------------------- |
| GET    | `/api/wallet`             | Return the current User's Wallet |
| GET    | `/api/wallet/balance`     | Return `balance` and `currency`  |
| GET    | `/api/beneficiaries`      | List owned beneficiaries         |
| POST   | `/api/beneficiaries`      | Create from `{name, phone}`      |
| GET    | `/api/beneficiaries/<id>` | Return one owned beneficiary     |
| PUT    | `/api/beneficiaries/<id>` | Update one owned beneficiary     |
| DELETE | `/api/beneficiaries/<id>` | Delete one owned beneficiary     |

### Nasra: Transactions and Admin

| Method | Endpoint                  | Responsibility                                   |
| ------ | ------------------------- | ------------------------------------------------ |
| POST   | `/api/transactions`       | Create a transfer                                |
| GET    | `/api/transactions`       | List current User's transactions and filters     |
| GET    | `/api/transactions/<id>`  | Return an authorized transaction detail          |
| GET    | `/api/admin/users`        | Return users, balances, counts, and statuses     |
| GET    | `/api/admin/transactions` | Search platform transactions                     |
| GET    | `/api/admin/analytics`    | Return volume, revenue, growth, and active users |

Transfer input accepts a recipient ID or phone, `amount`, and optional
`description`. Check balance and update balances atomically. Admin routes
require both a valid JWT and `role=admin`.

### Myles: Foundation and M-PESA

| Method | Endpoint              | Responsibility                                     |
| ------ | --------------------- | -------------------------------------------------- |
| GET    | `/api/health`         | Confirm that the backend is running                |
| POST   | `/api/mpesa/stk-push` | Start wallet funding from `{phone_number, amount}` |
| POST   | `/api/mpesa/callback` | Process the Daraja payment callback                |

Myles owns `app/__init__.py`, `config.py`, `run.py`, environment setup, and
the shared extension configuration. M-PESA services must use server-side
Daraja credentials and initially record funding as `pending`.

An accepted STK request is not proof of payment. Only a verified successful
callback may credit the Wallet. Callback handling must be idempotent so a
duplicate callback cannot credit the same Wallet twice.

## Service Responsibilities

`app/services.py` is divided by feature:

- Mason: `register_user`, `login_user`, `get_current_user`, `update_profile`
- Naomi: wallet, balance, and beneficiary CRUD services
- Nasra: transaction, history, detail, and admin services
- Myles: `get_mpesa_access_token`, `initiate_stk_push`, and
  `handle_mpesa_callback`

External Daraja requests must be mockable in tests. Keep route handlers small
and keep database transactions inside the service layer.

## Git Workflow

```text
main
├── backend-auth          # Mason
├── backend-wallet        # Naomi
├── backend-transactions  # Nasra
└── backend-mpesa         # Myles
```

Work on the assigned branch, make focused commits, pull the latest `main`, and
avoid editing another person's section at the same time. Myles reviews and
merges branches.

## Implementation Order

1. Myles confirms the app factory, configuration, health route, and Pipenv setup.
2. The team agrees on model fields, relationships, statuses, and money rules.
3. Mason implements authentication and profile APIs.
4. Naomi implements wallet and beneficiary APIs.
5. Nasra implements transfer and admin APIs.
6. Myles integrates Daraja sandbox STK Push and callbacks.
7. The frontend replaces localStorage actions with API requests.
8. The team runs tests and completes the registration-to-wallet-funding demo.

## Testing

```bash
pipenv run pytest
```

Tests must cover successful and invalid requests, JWT verification, roles,
ownership, model relationships, balance checks, transaction statuses, M-PESA
failures, and duplicate callbacks. Mock all external Daraja calls.

## Frontend Integration

The React frontend provides registration, login, profile, dashboard, wallet,
beneficiary, transfer, transaction-history, and admin pages. Replace each
localStorage operation with its matching API request above. Send the JWT as a
bearer token, handle `401` by returning the user to login, and display API
validation errors in the relevant form.
