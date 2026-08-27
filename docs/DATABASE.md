# PesaFlow database setup

## Local development

The project uses SQLite by default, so no database server is needed for local
development. From the repository root, run:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

The first command creates `db.sqlite3`. The second command asks for the
administrator's email, phone, full name, and password. Sign in at
`http://127.0.0.1:8000/admin/`. The local health endpoint is
`http://127.0.0.1:8000/api/`.

To use PostgreSQL instead, add a `DATABASE_URL` to `.env` before migrating:

```text
DATABASE_URL=postgresql://pesaflow_user:password@localhost:5432/pesaflow
```

Never commit `.env` or real credentials.

## Database diagram

`User` is the only table created today. The other tables below are the agreed
design for the team; their owners will add the actual Django models and
migrations. This keeps the diagram useful without claiming unfinished tables
already exist.

```mermaid
erDiagram
    USER {
        bigint id PK
        string email UK
        string phone UK
        string full_name
        string role
        boolean is_active
        boolean is_staff
        datetime created_at
    }
    WALLET {
        bigint id PK
        bigint user_id FK_UK
        decimal balance
        string currency
    }
    BENEFICIARY {
        bigint id PK
        bigint user_id FK
        string name
        string phone
    }
    TRANSACTION {
        bigint id PK
        bigint sender_id FK
        bigint recipient_id FK
        decimal amount
        decimal fee
        string status
        string reference UK
    }
    MPESA_TRANSACTION {
        bigint id PK
        bigint transaction_id FK
        string phone
        decimal amount
        string checkout_request_id UK
        string status
    }
    USER ||--o| WALLET : "will own"
    USER ||--o{ BENEFICIARY : "will save"
    USER ||--o{ TRANSACTION : "will send"
    USER ||--o{ TRANSACTION : "will receive"
    TRANSACTION ||--o| MPESA_TRANSACTION : "may have"
```

### Relationship summary

| Relationship | Meaning |
| --- | --- |
| User → Wallet | One user has one wallet. `user_id` is unique. |
| User → Beneficiary | One user can save many recipients. |
| User → Transaction | A user can send and receive many transactions. |
| Transaction → MpesaTransaction | A transfer or funding record may have one M-PESA record. |

`PK` means primary key, `FK` means foreign key, and `UK` means unique key.
