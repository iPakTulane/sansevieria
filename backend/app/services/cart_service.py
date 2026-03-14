from sqlalchemy.orm import Session
from app.models.cart import Cart, CartItem
from app.models.product import Product

def get_cart_for_user(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def add_item_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1):
    cart = get_cart_for_user(db, user_id)
    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    db.refresh(cart)
    return cart

def remove_item_from_cart(db: Session, user_id: int, item_id: int):
    cart = get_cart_for_user(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if item:
        db.delete(item)
        db.commit()
        db.refresh(cart)
    return cart

def clear_cart(db: Session, user_id: int):
    cart = get_cart_for_user(db, user_id)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
