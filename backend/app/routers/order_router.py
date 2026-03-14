from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.order_schema import OrderResponse, CheckoutRequest
from app.services.order_service import create_order_from_cart, get_user_orders, get_order
from app.routers.auth_router import get_current_user
from app.models.user import User

order_router = APIRouter()
checkout_router = APIRouter()

@order_router.get("/", response_model=List[OrderResponse])
def read_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_orders(db, current_user.id)

@order_router.get("/{order_id}", response_model=OrderResponse)
def read_order(order_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@checkout_router.post("/", response_model=OrderResponse)
def checkout(checkout_data: CheckoutRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Basic logic to convert cart to order
    try:
        order = create_order_from_cart(db, current_user.id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
