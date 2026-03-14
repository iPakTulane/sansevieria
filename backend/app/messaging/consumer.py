import json
import time
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models.order import Order
from app.messaging.queues import EMAIL_NOTIFICATION_QUEUE
from app.messaging.producer import publish_message
from app.services.order_state_service import update_order_state

logger = logging.getLogger("ORDER_PROCESSOR")

def process_order(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    correlation_id = properties.headers.get("correlation_id") if properties.headers else payload.get("correlation_id", order_id_str)
    
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Received ORDER_CREATED'")
    
    db = SessionLocal()
    try:
        # Atomic transition to PROCESSING
        order = update_order_state(db, order_id_str, "PROCESSING", correlation_id)
        
        # Simulate processing time
        time.sleep(3)
        
        # Atomic transition to COMPLETED
        order = update_order_state(db, order_id_str, "COMPLETED", correlation_id)
        
        # Publish to email queue
        email_msg = {
            "event": "ORDER_COMPLETED",
            "order_id": order.order_id,
            "user_id": order.user_id,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        publish_message(EMAIL_NOTIFICATION_QUEUE, email_msg, correlation_id=correlation_id)
    except Exception as e:
        logger.error(f"[ORDER_PROCESSOR] correlation_id={correlation_id} error='Processing failed' details={str(e)}")
        # Optionally transition to FAILED state if this was a known exception 
        # But letting it fail and nack can also be valid if we want to retry. 
        # We will atomic update to FAILED for demonstration.
        try:
            update_order_state(db, order_id_str, "FAILED", correlation_id)
        except Exception as rollback_err:
            logger.error(f"[ORDER_PROCESSOR] correlation_id={correlation_id} error='Failed to set FAILED status' details={str(rollback_err)}")
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def process_email(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    correlation_id = properties.headers.get("correlation_id") if properties.headers else payload.get("correlation_id", order_id_str)
    
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Received ORDER_COMPLETED. Sending email...'")
    
    # Simulate sending email
    time.sleep(2)
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Email sent successfully'")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
