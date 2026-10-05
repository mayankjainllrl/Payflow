# PayFlow

A small payments service built to get the hard parts of moving money right: retries that never double-charge, and a ledger that always balances.

I work on payment systems professionally. PayFlow is where I rebuild those ideas on a modern async Python stack, in the open.

![CI](https://github.com/mayankjainllrl/Payflow/actions/workflows/ci.yml/badge.svg)

## What it does today

- **`POST /payments`** creates a payment and its ledger entries.
- **Idempotent by design.** Every request carries an `Idempotency-Key` header. Sending the same key again returns the original payment instead of creating a second one.
- **Safe under a race.** Two requests with the same key can arrive at the same moment and both pass the "does it exist?" check. A unique constraint on the key lets the database pick one winner; the loser catches the `IntegrityError`, rolls back and returns the winner's payment.
- **Double-entry ledger.** Each payment writes two balanced entries (a debit and a credit) in the same transaction as the payment itself. Either all three rows are saved or none are.
- **Money as integer cents.** Amounts are stored as `amount_cents`, never as floats.
- **Tested against a real database.** Async integration tests run against PostgreSQL, locally and in GitHub Actions.

## Stack

| Area | Tools |
|---|---|
| API | FastAPI, Pydantic v2 |
| Database | PostgreSQL 16, SQLAlchemy 2.0 (async), asyncpg |
| Migrations | Alembic |
| Tests | pytest, pytest-asyncio, httpx |
| Tooling | uv, Docker, docker-compose, GitHub Actions |

## Design decisions

**Why a unique constraint and not just a lookup?**
Checking for an existing key and then inserting is two steps, and two requests can both finish step one before either does step two. The application cannot close that gap on its own. The database can: with a unique constraint, only one insert succeeds.

**Why one transaction for the payment and the ledger?**
A payment without ledger entries, or ledger entries without a payment, means the books are wrong. Writing all three rows in one transaction makes that state impossible.

**Why integer cents?**
Floating-point numbers cannot represent most decimal amounts exactly, and the errors add up. Integers do not drift.

## Run it locally

You need Docker and [uv](https://docs.astral.sh/uv/).

```bash
# start the API and PostgreSQL
docker compose up -d --build

# create the tables
uv sync --dev
uv run alembic upgrade head
```

The API is now on `http://localhost:8000` (interactive docs at `/docs`).

```bash
curl -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: order-123" \
  -d '{"amount_cents": 5000}'
```

Run the same command twice: you get the same payment `id` both times.

## Run the tests

The integration tests use a separate `payflow_test` database.

```bash
docker compose exec db createdb -U payflow payflow_test
uv run pytest -v
```

## Project layout

```
app/
  api/        routes and request schemas
  core/       settings and database session
  models/     Payment and LedgerEntry
migrations/   Alembic migrations
tests/        health, validation and idempotency tests
```

## Roadmap

Not built yet, in the order I plan to do them:

1. Stripe test-mode integration and signed webhook handling
2. Payment status transitions driven by webhooks
3. Reconciliation between the ledger and the processor
4. Redis for rate limiting and caching
5. Deployment to AWS with infrastructure as code

## Author

Mayank Jain · [Portfolio](https://mayankjainllrl.github.io) · [LinkedIn](https://www.linkedin.com/in/mayank-jain-731325148/)
