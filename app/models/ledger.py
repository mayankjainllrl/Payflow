
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.payment import Base

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id"))
    account: Mapped[str]
    direction: Mapped[str]          # "debit" | "credit"
    amount_cents: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    