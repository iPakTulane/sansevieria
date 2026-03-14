import pika
from app.config import settings
from app.messaging.queues import ORDER_PROCESSING_QUEUE, EMAIL_NOTIFICATION_QUEUE

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def setup_queues():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue=ORDER_PROCESSING_QUEUE, durable=True)
        channel.queue_declare(queue=EMAIL_NOTIFICATION_QUEUE, durable=True)
        connection.close()
        print("RabbitMQ queues setup successfully.")
    except Exception as e:
        print(f"RabbitMQ Setup Error: {e}")
