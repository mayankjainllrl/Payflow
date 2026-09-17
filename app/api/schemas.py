from pydantic import BaseModel

class PaymentCreate(BaseModel):
    amount_cents: int 
    currency: str = "usd"