from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import PaymentCreate
from app.core.db import get_session
from app.models.payment import Payment
from app.models.ledger import LedgerEntry

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/payments", status_code=201)
async def create_payment(body: PaymentCreate, idempotency_key: str = Header(), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Payment).where(Payment.idempotency_key == idempotency_key)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"id": str(existing.id), "status": existing.status}
    
    payment = Payment(amount_cents=body.amount_cents, currency=body.currency, idempotency_key=idempotency_key)
    session.add(payment)
    await session.flush()
    session.add(LedgerEntry(payment_id=payment.id, account="customer_funds", direction="debit", amount_cents=body.amount_cents))
    session.add(LedgerEntry(payment_id=payment.id, account="platform_receivable", direction="credit", amount_cents=body.amount_cents))
    await session.commit()
    
    return {"id": str(payment.id), "status": payment.status}