import pika
import sys
import os

# Ensure the parent directory is in sys.path when running as a stand-alone script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.messaging.rabbitmq import get_rabbitmq_connection, setup_queues
from app.messaging.queues import ORDER_PROCESSING_QUEUE, EMAIL_NOTIFICATION_QUEUE
from app.messaging.consumer import process_order, process_email
from app.workflow.workflow_service import workflow_worker

def main():
    setup_queues()
    workflow_worker.start()  # Start BPMN poller
    
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    # Prefetch count ensures worker doesn't get overwhelmed
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue=ORDER_PROCESSING_QUEUE, on_message_callback=process_order)
    channel.basic_consume(queue=EMAIL_NOTIFICATION_QUEUE, on_message_callback=process_email)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        workflow_worker.stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

