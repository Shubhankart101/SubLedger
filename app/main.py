from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.routes import customers, invoices, payments, plans, subscriptions
from app.core.errors import DomainError
from app.db import Base, engine
from app import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SubLedger", version="1.0.0", description="A layered SaaS billing backend")
app.include_router(plans.router)
app.include_router(customers.router)
app.include_router(subscriptions.router)
app.include_router(invoices.router)
app.include_router(payments.router)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "A conflicting record already exists"})


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}