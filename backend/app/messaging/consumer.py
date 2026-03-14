import json
import time
from datetime import datetime
from app.database import SessionLocal
from app.models.order import Order
from app.messaging.queues import EMAIL_NOTIFICATION_QUEUE
from app.messaging.producer import publish_message

def process_order(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    print(f" [x] Received ORDER_CREATED for {order_id_str}")
    
    db = SessionLocal()
    order = db.query(Order).filter(Order.order_id == order_id_str).first()
    
    if order:
        order.status = "PROCESSING"
        db.commit()
        
        # Simulate processing time
        time.sleep(3)
        
        order.status = "COMPLETED"
        db.commit()
        print(f" [x] Order {order_id_str} processed successfully.")
        
        # Publish to email queue
        email_msg = {
            "event": "ORDER_COMPLETED",
            "order_id": order.order_id,
            "user_id": order.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        publish_message(EMAIL_NOTIFICATION_QUEUE, email_msg)
    else:
        print(f" [!] Order {order_id_str} not found in database.")
    
    db.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

def process_email(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    print(f" [x] Received ORDER_COMPLETED for {order_id_str}. Sending email...")
    
    # Simulate sending email
    time.sleep(2)
    print(f" [x] Email sent successfully for order {order_id_str}.")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
