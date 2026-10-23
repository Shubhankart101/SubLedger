# Local Development

## Prerequisites

- Python 3.11 or newer.
- Docker Desktop with Compose, if using the container workflow.

## Windows PowerShell Setup

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000`, Swagger UI is `/docs`, and OpenAPI JSON is `/openapi.json`. The default SQLite database file is `subledger.db` in the working directory.

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./subledger.db` | SQLAlchemy connection URL |
| `APP_ENV` | `development` | Runtime environment label |

The app loads `.env` through `python-dotenv`. Do not commit local `.env` files or real credentials.

For PostgreSQL, install the declared psycopg dependency and set `DATABASE_URL`, for example `postgresql+psycopg://user:password@localhost:5432/subledger`.

## Docker Compose

```powershell
docker compose up --build
```

Compose maps port 8000 and stores the SQLite file in the named `subledger-data` volume. `docker compose down` stops the service; the named volume remains unless explicitly removed.

## Useful Commands

```powershell
python -m pytest -q
python -m uvicorn app.main:app --reload
docker build -t subledger:local .
```
