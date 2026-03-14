import json
import pika
from app.messaging.rabbitmq import get_rabbitmq_connection
import logging

logger = logging.getLogger("ORDER_PROCESSOR")

def publish_message(queue_name: str, message: dict, correlation_id: str = None):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        properties = pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            headers={"correlation_id": correlation_id} if correlation_id else {}
        )
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=properties
        )
        if correlation_id:
            logger.info(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Message published' queue={queue_name}")
            
        connection.close()
        return True
    except Exception as e:
        if correlation_id:
            logger.error(f"[ORDER_PROCESSOR] correlation_id={correlation_id} msg='Publish failed' queue={queue_name} error={str(e)}")
        print(f"Error publishing message to {queue_name}: {e}")
        return False
