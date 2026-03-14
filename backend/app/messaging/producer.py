import json
import pika
from app.messaging.rabbitmq import get_rabbitmq_connection

def publish_message(queue_name: str, message: dict):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Error publishing message to {queue_name}: {e}")
        return False
