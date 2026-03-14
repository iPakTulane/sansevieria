from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .product_schema import ProductResponse

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float
    product: ProductResponse
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_id: str
    user_id: int
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
        
class CheckoutRequest(BaseModel):
    full_name: str
    shipping_address: str
    city: str
    postal_code: str
    card_number: str
    expiry_date: str
    cvv: str
