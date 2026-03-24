import pika
from app.config import settings
from app.messaging.queues import ORDER_PROCESSING_QUEUE, EMAIL_NOTIFICATION_QUEUE, ORDER_PROCESSING_DLQ, EMAIL_NOTIFICATION_DLQ

import time

def get_rabbitmq_connection(retries=5, delay=5):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials
    )
    for i in range(retries):
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ connection failed (attempt {i+1}/{retries}). Retrying in {delay}s...")
            time.sleep(delay)
    return pika.BlockingConnection(parameters)

def setup_queues():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare DLQs
        channel.queue_declare(queue=ORDER_PROCESSING_DLQ, durable=True)
        channel.queue_declare(queue=EMAIL_NOTIFICATION_DLQ, durable=True)
        
        # Declare main queues with DLX args
        channel.queue_declare(queue=ORDER_PROCESSING_QUEUE, durable=True, arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": ORDER_PROCESSING_DLQ
        })
        channel.queue_declare(queue=EMAIL_NOTIFICATION_QUEUE, durable=True, arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": EMAIL_NOTIFICATION_DLQ
        })
        
        connection.close()
        print("RabbitMQ queues and DLQs setup successfully.")
    except Exception as e:
        print(f"RabbitMQ Setup Error: {e}")
