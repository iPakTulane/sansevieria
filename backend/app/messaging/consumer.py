import json
import time
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models.order import Order
from app.messaging.queues import EMAIL_NOTIFICATION_QUEUE
from app.messaging.producer import publish_message
from app.services.order_state_service import update_order_state
from app.workflow.camunda_client import camunda_client

logger = logging.getLogger("ORDER_PROCESSOR")

def process_order(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    correlation_id = properties.headers.get("correlation_id") if properties.headers else payload.get("correlation_id", order_id_str)
    
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Received ORDER_CREATED, triggering BPMN workflow'")
    
from app.utils.fault_handlers import with_retries

@with_retries(max_retries=3, base_delay=1)
def invoke_camunda(correlation_id: str, order_id_str: str):
    response = camunda_client.start_process_instance(
        process_key="OrderFulfillmentProcess", 
        business_key=correlation_id,
        variables={"order_id": order_id_str}
    )
    if not response:
        raise Exception("Failed to start Camunda workflow instance")
    return response

def process_order(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    correlation_id = properties.headers.get("correlation_id") if properties.headers else payload.get("correlation_id", order_id_str)
    
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Received ORDER_CREATED, triggering BPMN workflow'")
    
    try:
        response = invoke_camunda(correlation_id, order_id_str)
        logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Started workflow instance {response.get('id')}'")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Fatal workflow start failure. Routing to DLQ. Error: {e}'")
        # Reject without requeue triggers DLX routing
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

def process_email(ch, method, properties, body):
    payload = json.loads(body)
    order_id_str = payload.get("order_id")
    correlation_id = properties.headers.get("correlation_id") if properties.headers else payload.get("correlation_id", order_id_str)
    
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Received ORDER_COMPLETED. Sending email...'")
    
    # Simulate sending email
    time.sleep(2)
    logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Email sent successfully'")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
