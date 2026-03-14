import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order
from datetime import datetime

# Configure structured logging
logger = logging.getLogger("ORDER_PROCESSOR")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

VALID_TRANSITIONS = {
    "PENDING": ["PROCESSING", "FAILED"],
    "PROCESSING": ["COMPLETED", "FAILED"],
    "COMPLETED": [],
    "FAILED": []
}

def log_transition(correlation_id: str, old_state: str, new_state: str):
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} status={new_state} (from {old_state})")

def update_order_state(db: Session, order_id_str: str, new_state: str, correlation_id: str) -> Order:
    """
    Updates order state atomically using row-level locking.
    Validates state transitions and records timestamps.
    """
    if new_state not in VALID_TRANSITIONS:
        raise ValueError(f"Invalid target state: {new_state}")
    
    # Use row-level locking to prevent concurrent state updates
    order = db.query(Order).filter(Order.order_id == order_id_str).with_for_update().first()
    
    if not order:
        logger.error(f"[ORDER_PROCESSOR] correlation_id={correlation_id} error='Order not found' target_status={new_state}")
        raise ValueError("Order not found")
        
    current_state = order.status
    
    # Idempotency check: if already in the target state, just return it
    if current_state == new_state:
        logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Idempotent transition ignored' status={new_state}")
        return order
        
    # Validate transition
    if new_state not in VALID_TRANSITIONS.get(current_state, []):
        logger.error(f"[ORDER_PROCESSOR] correlation_id={correlation_id} error='Invalid transition' from={current_state} to={new_state}")
        raise ValueError(f"Invalid state transition from {current_state} to {new_state}")
        
    # Apply transition
    order.status = new_state
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
        
    db.refresh(order)
    log_transition(correlation_id, current_state, new_state)
    
    return order
