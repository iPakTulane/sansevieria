from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.services.cart_service import get_cart_for_user, clear_cart
from app.utils.identifiers import generate_order_id

def create_order_from_cart(db: Session, user_id: int):
    cart = get_cart_for_user(db, user_id)
    if not cart.items:
        raise ValueError("Cart is empty")
    
    total_amount = sum([item.product.price * item.quantity for item in cart.items])
    order = Order(
        order_id=generate_order_id(),
        user_id=user_id,
        status="pending",
        total_amount=total_amount
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        )
        db.add(order_item)
    
    db.commit()
    clear_cart(db, user_id)
    db.refresh(order)
    return order

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_order(db: Session, order_id: str, user_id: int):
    return db.query(Order).filter(Order.order_id == order_id, Order.user_id == user_id).first()
