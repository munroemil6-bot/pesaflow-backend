# PesaFlow Backend

PesaFlow is a Flask REST API for a money-transfer application. It will provide
secure authentication, user profiles, wallets, beneficiaries, transfers,
M-PESA funding, and an administrator workspace for the PesaFlow React frontend.

The frontend currently uses a browser `localStorage` mock database for
demonstration. The completed backend will replace that mock data with a shared
PostgreSQL database and authenticated HTTP/JSON requests.

## Technology

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-CORS
- Marshmallow
- PostgreSQL with `psycopg2-binary`
- Requests for Safaricom Daraja API calls
- Pytest for automated tests

## Project Structure

```text
pesaflow-backend/
├── app/
│   ├── __init__.py       # Flask extensions and application factory
│   ├── models.py         # SQLAlchemy database models and relationships
│   ├── schemas.py        # JSON input validation and response serialization
│   ├── routes.py         # Direct @app REST route registration
│   └── services.py       # Business logic and Daraja API communication
├── migrations/           # Database migration revisions
├── tests/                # Feature and integration tests
├── .env                 # Local secrets; never commit this file
├── .env.example         # Required environment variable names
├── config.py             # Environment-backed Flask configuration
├── run.py               # Local development entry point
├── Pipfile              # Pipenv dependencies
└── Pipfile.lock         # Locked dependency versions
```

## Local Setup

Install Python 3.12 and Pipenv, then run these commands from this directory:

```bash
pipenv --python 3.12
pipenv install
pipenv install --dev pytest
cp .env.example .env
pipenv run python run.py
```

The API will run at `http://127.0.0.1:5000`.

Check that the application is running:

```bash
curl http://127.0.0.1:5000/api/health
```

Expected response:

```json
{ "service": "pesaflow-backend", "status": "ok" }
```

## Configuration and Security

Copy `.env.example` to `.env` and add local values for the database, JWT, and
Daraja sandbox credentials. Never commit `.env`, passwords, consumer secrets,
passkeys, or JWT secrets. The frontend must never receive M-PESA credentials.

Required configuration includes:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `MPESA_CONSUMER_KEY`
- `MPESA_CONSUMER_SECRET`
- `MPESA_SHORTCODE`
- `MPESA_PASSKEY`
- `MPESA_CALLBACK_URL`
- `MPESA_ENVIRONMENT=sandbox`

## Architecture Rules

The backend is a REST API. Every feature route should use an HTTP method,
JSON request data, JSON response data, and the correct HTTP status code.

Routes are registered directly on the Flask application. Do not create or use
Flask blueprints in this project. Add feature handlers inside
`register_routes(app)` in `app/routes.py` using decorators such as:

```python
@app.post("/api/example")
def example():
	...
```

Keep route handlers thin. They should authenticate the request, validate input,
call a service, and return a response. Database changes and business rules
belong in `app/services.py`.

Use these status codes consistently:

- `200` for successful reads and updates
- `201` for successful creation
- `204` for successful deletion with no response body
- `400` for invalid JSON or validation errors
- `401` for missing or invalid JWT credentials
- `403` for an authenticated user without permission
- `404` when a requested record does not exist or is not visible
- `409` for duplicate or conflicting data

## Database Models and Relationships

The following SQLAlchemy models will support the frontend workflows:

### User

Stores `id`, `full_name`, `email`, `phone`, `password_hash`, `role`, account
status, and timestamps.

- One `User` has one `Wallet`.
- One `User` has many `Beneficiary` records.
- One `User` can send many `Transaction` records.
- One `User` can receive many `Transaction` records.

### Wallet

Stores `user_id`, `balance`, `currency`, and timestamps. `user_id` is a unique
foreign key to `User.id`, so each user has one wallet.

### Beneficiary

Stores `user_id`, beneficiary name, phone number, and creation time. A
beneficiary belongs to one user and must only be visible to that owner.

### Transaction

Stores sender, recipient, amount, fee, total amount, status, reference,
description, transaction type, and creation time. Both `sender_id` and
`recipient_id` reference `User.id`.

### MpesaTransaction

Stores the related transaction, phone number, amount, Daraja request IDs,
receipt number, result code, result description, status, and timestamps. Each
M-PESA record belongs to one transaction.

Money must use a fixed-precision numeric database type, not floating-point
values. Add foreign-key constraints, useful indexes, and migration support.

## API Contract

All protected endpoints require:

```text
Authorization: Bearer <jwt-access-token>
```

### Mason: Authentication and Profile

| Method | Endpoint             | Purpose                                                               |
| ------ | -------------------- | --------------------------------------------------------------------- |
| `POST` | `/api/auth/register` | Validate registration data, hash the password, create User and Wallet |
| `POST` | `/api/auth/login`    | Verify credentials and return a JWT access token                      |
| `GET`  | `/api/auth/me`       | Return the authenticated user                                         |
| `GET`  | `/api/users/me`      | Return the authenticated profile                                      |
| `PUT`  | `/api/users/me`      | Update allowed profile fields                                         |

Registration input should contain `full_name`, `email`, `phone`, and `password`.
Passwords must be hashed and must never be returned in JSON.

### Nasra: Wallet and Beneficiaries

| Method   | Endpoint                  | Purpose                                           |
| -------- | ------------------------- | ------------------------------------------------- |
| `GET`    | `/api/wallet`             | Return the authenticated user wallet              |
| `GET`    | `/api/wallet/balance`     | Return `balance` and `currency` for the dashboard |
| `GET`    | `/api/beneficiaries`      | List the current user's beneficiaries             |
| `POST`   | `/api/beneficiaries`      | Create from `{name, phone}`                       |
| `GET`    | `/api/beneficiaries/<id>` | Return one owned beneficiary                      |
| `PUT`    | `/api/beneficiaries/<id>` | Update one owned beneficiary                      |
| `DELETE` | `/api/beneficiaries/<id>` | Delete one owned beneficiary                      |

### Naomi: Transfers and Admin

| Method | Endpoint                  | Purpose                                                 |
| ------ | ------------------------- | ------------------------------------------------------- |
| `POST` | `/api/transactions`       | Create a transfer using recipient and amount data       |
| `GET`  | `/api/transactions`       | List the user's transactions with filters               |
| `GET`  | `/api/transactions/<id>`  | Show a transaction to its sender or recipient           |
| `GET`  | `/api/admin/users`        | List users, balances, counts, and account statuses      |
| `GET`  | `/api/admin/transactions` | Search platform transactions and statuses               |
| `GET`  | `/api/admin/analytics`    | Return volume, revenue, growth, and active-user metrics |

Transfer input should contain a recipient ID or phone number, `amount`, and an
optional `description`. Check balance, prevent self-transfer if required by the
team rules, create the transaction, and update balances atomically.

Admin endpoints require both a valid JWT and `role=admin`.

### Myles: M-PESA and Integration Foundation

| Method | Endpoint              | Purpose                                            |
| ------ | --------------------- | -------------------------------------------------- |
| `GET`  | `/api/health`         | Confirm that the API is running                    |
| `POST` | `/api/mpesa/stk-push` | Start wallet funding with `{phone_number, amount}` |
| `POST` | `/api/mpesa/callback` | Receive and process the Daraja callback            |

The STK endpoint communicates with Safaricom Daraja from the server. It must
create a pending record before returning. An accepted STK request is not proof
of payment. Only a verified successful callback may mark the payment successful
and increase the wallet balance. Callback processing must be idempotent so a
duplicate callback cannot credit the wallet twice.

During local development, use a secure tunnel such as ngrok for the callback.
Do not treat a temporary tunnel as the production deployment architecture.

## Work Allocation

### Myles Munroe: Project Leader and M-PESA

- Maintain `app/__init__.py`, `config.py`, `run.py`, and environment setup.
- Maintain the shared SQLAlchemy, migration, JWT, CORS, and configuration foundation.
- Implement M-PESA access-token, STK-push, and callback services.
- Coordinate shared edits and review migrations before merging.
- Own `tests/test_mpesa.py` and integration checks.

### Mason: Authentication and Profile

- Implement the User model and authentication/profile schemas.
- Add password hashing, login verification, JWT creation, and current-user checks.
- Implement the authentication and profile routes and services.
- Own `tests/test_auth.py`.

### Nasra: Wallet and Beneficiaries

- Implement Wallet and Beneficiary models and ownership relationships.
- Implement wallet, balance, and beneficiary schemas, services, and routes.
- Ensure users cannot read or modify another user's wallet or beneficiaries.
- Own `tests/test_wallet.py`.

### Naomi: Transactions and Admin

- Implement the Transaction model, sender/recipient relationships, and schemas.
- Implement transfer, history, detail, and admin routes and services.
- Enforce balance checks, transaction visibility, and admin authorization.
- Own `tests/test_transactions.py`.

## Git Workflow

Create one branch per responsibility:

```text
main
├── backend-auth
├── backend-wallet
├── backend-transactions
└── backend-mpesa
```

Commit focused changes, pull the latest `main` before starting work, and avoid
editing another member's section at the same time. Myles reviews and merges the
branches into `main`.

## Implementation Order

1. Myles confirms the environment, app factory, configuration, and health API.
2. The team agrees on model fields, relationships, status values, and money rules.
3. Mason implements authentication and profile access.
4. Nasra implements wallets and beneficiaries.
5. Naomi implements transfers and admin reporting.
6. Myles integrates Daraja sandbox funding and callbacks.
7. The team replaces frontend mock data with backend API requests.
8. The team runs the full test suite and completes the registration-to-wallet-funding demo.

## Testing

Run the current test command with:

```bash
pipenv run pytest
```

Tests should cover successful requests, validation failures, authentication,
authorization, ownership, database relationships, transaction status changes,
M-PESA failures, and duplicate callbacks. External Daraja requests must be
mocked in tests.

## Frontend Integration

The React frontend contains user pages for registration, login, profile,
dashboard, wallet, beneficiaries, transfers, and transaction history. It also
contains protected admin pages for dashboard metrics, users, transactions, and
analytics.

Replace each localStorage action with a request to the matching endpoint above.
Store the JWT securely on the client, send it as a bearer token, handle `401`
responses by returning the user to login, and display API validation errors in
the relevant form.
