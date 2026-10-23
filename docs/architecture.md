# Application Architecture

## Runtime Structure

```mermaid
flowchart LR
    Consumer --> Route[FastAPI route]
    Route --> Schema[Pydantic request/response schema]
    Route --> Dependency[FastAPI dependency composition]
    Dependency --> Service[Application service]
    Service --> Repository[Repository]
    Repository --> Session[SQLAlchemy session]
    Session --> Database[(Relational database)]
    Service --> Ledger[Ledger service]
```

Routes handle HTTP transport and status models, not billing decisions. `app/api/dependencies.py` creates services with a request-scoped SQLAlchemy session and the repositories they need. Services enforce domain rules and commit complete operations. Repositories own SQL queries and persistence. `app/models.py` declares relational entities, while `app/schemas.py` validates API data.

## Domain Components

- `Plan`: price, currency, billing cycle, and active/inactive availability.
- `Customer`: unique email and customer profile.
- `Subscription`: customer/plan relationship, lifecycle status, and next billing date.
- `Invoice`: customer/subscription, billing period, price snapshot, balance, status, and due date.
- `PaymentAttempt`: immutable record of a successful or failed payment attempt.
- `LedgerEntry`: append-oriented audit event with a reference to its source operation.

The entity relationships and ownership tables are maintained in [DESIGN.md](../DESIGN.md).

## Transaction Boundaries

Invoice creation inserts an invoice, records `invoice_created`, and advances the next billing date in one SQLAlchemy transaction. Payment recording inserts an attempt, updates invoice balance/status on success only, and records its matching ledger event in one transaction. A failed attempt never increments `amount_paid`.

## Error Handling

Known domain errors are mapped to 404, 409, or 422 responses. Database integrity conflicts are returned as HTTP 409. Request shape and basic numeric constraints are validated by Pydantic before service execution.

## Persistence

SQLite is the local default. Set `DATABASE_URL` to a SQLAlchemy database URL. PostgreSQL requires the included psycopg 3 driver and a URL such as `postgresql+psycopg://user:password@host:5432/database`. Table creation uses `Base.metadata.create_all` for this starter; schema evolution should use Alembic migrations.
