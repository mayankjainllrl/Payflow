from fastapi import APIRouter, Depends
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
async def create_payment(body: PaymentCreate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        payment = Payment(amount_cents=body.amount_cents, currency=body.currency)
        session.add(payment)
        await session.flush()
        session.add(LedgerEntry(payment_id=payment.id, account="customer_funds", direction="debit", amount_cents=1000))
        session.add(LedgerEntry(payment_id=payment.id, account="platform_receivable", direction="credit", amount_cents=1000))
    
    return {"id": str(payment.id), "status": payment.status}