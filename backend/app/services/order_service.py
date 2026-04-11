from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.services.cart_service import get_cart_for_user, clear_cart
from app.utils.identifiers import generate_order_id
from app.messaging.producer import publish_message
from app.messaging.queues import ORDER_PROCESSING_QUEUE
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger("ORDER_FLOW")

def create_order_from_cart(db: Session, user_id: int):
    cart = get_cart_for_user(db, user_id)
    if not cart.items:
        raise ValueError("Cart is empty")
    
    total_amount = sum([item.product.price * item.quantity for item in cart.items])
    order_id_str = generate_order_id()
    
    logger.info(
        order_id_str,
        order_id_str,
        "Creating order from cart",
        user_id=user_id,
        status="PENDING",
    )
    
    order = Order(
        order_id=order_id_str,
        user_id=user_id,
        status="PENDING",
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

    logger.info(
        order_id_str,
        order_id_str,
        "Order created",
        user_id=order.user_id,
        total_amount=round(float(order.total_amount or 0), 2),
        status=order.status,
    )
    
    # Publish to order queue
    publish_message(ORDER_PROCESSING_QUEUE, {
        "order_id": order.order_id,
        "user_id": order.user_id,
        "event": "ORDER_CREATED",
        "correlation_id": order.order_id,
        "timestamp": datetime.utcnow().isoformat()
    }, correlation_id=order.order_id)
    
    return order

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_order(db: Session, order_id: str, user_id: int):
    return db.query(Order).filter(Order.order_id == order_id, Order.user_id == user_id).first()
