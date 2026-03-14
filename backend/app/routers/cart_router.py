from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cart_schema import CartResponse, CartItemCreate
from app.services.cart_service import get_cart_for_user, add_item_to_cart, remove_item_from_cart
from app.routers.auth_router import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=CartResponse)
def read_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_cart_for_user(db, current_user.id)

@router.post("/", response_model=CartResponse)
def add_to_cart(cart_item: CartItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return add_item_to_cart(db, current_user.id, cart_item.product_id, cart_item.quantity)

@router.delete("/{item_id}", response_model=CartResponse)
def delete_from_cart(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return remove_item_from_cart(db, current_user.id, item_id)
