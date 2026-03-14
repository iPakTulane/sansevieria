import time
import logging
import threading
from app.workflow.camunda_client import camunda_client
from app.database import SessionLocal
from app.services.order_state_service import update_order_state
from app.messaging.producer import publish_message
from app.messaging.queues import EMAIL_NOTIFICATION_QUEUE
from datetime import datetime

logger = logging.getLogger("ORDER_PROCESSOR")

class WorkflowWorker:
    def __init__(self, worker_id="python-worker"):
        self.worker_id = worker_id
        self.running = False
        
    def start(self):
        self.running = True
        topics = [
            ("validate_order", self.validate_order),
            ("process_payment", self.process_payment),
            ("reserve_inventory", self.reserve_inventory),
            ("generate_shipment", self.generate_shipment),
            ("generate_invoice", self.generate_invoice),
            ("send_confirmation", self.send_confirmation)
        ]
        
        # Start a thread for polling topics
        def poll_loop():
            while self.running:
                for topic, handler in topics:
                    try:
                        tasks = camunda_client.fetch_and_lock(self.worker_id, topic)
                        for task in tasks:
                            order_id = task.get("businessKey") or self._extract_var(task, "order_id")
                            if not order_id:
                                logger.error(f"[BPMN] Topic {topic} failed - no order_id correlation found in task {task.get('id')}")
                                camunda_client.complete_task(task.get("id"), self.worker_id)
                                continue
                                
                            logger.info(f"[BPMN] Executing task {topic} correlation_id={order_id}")
                            try:
                                handler(order_id)
                                camunda_client.complete_task(task["id"], self.worker_id)
                                logger.info(f"[BPMN] Completed task {topic} correlation_id={order_id}")
                            except Exception as e:
                                logger.error(f"[BPMN] Task error {topic} correlation_id={order_id}: {str(e)}")
                    except Exception:
                        pass
                time.sleep(2)
                
        self.thread = threading.Thread(target=poll_loop, daemon=True)
        self.thread.start()
        logger.info("[BPMN] Started external task workers")

    def stop(self):
        self.running = False

    def _extract_var(self, task, var_name):
        variables = task.get("variables", {})
        if var_name in variables:
            return variables[var_name].get("value")
        return None

    # Service implementations
    def validate_order(self, order_id: str):
        db = SessionLocal()
        try:
            # We enforce PENDING -> PROCESSING transition here
            update_order_state(db, order_id, "PROCESSING", order_id)
            logger.info(f"[BPMN] Validated order correlation_id={order_id}")
        finally:
            db.close()

    def process_payment(self, order_id: str):
        logger.info(f"[BPMN] Processing payment correlation_id={order_id}")
        time.sleep(1) # simulate external payment

    def reserve_inventory(self, order_id: str):
        logger.info(f"[BPMN] Reserving inventory correlation_id={order_id}")
        time.sleep(1) # simulate inventory check

    def generate_shipment(self, order_id: str):
        logger.info(f"[BPMN] Generating shipment correlation_id={order_id}")
        time.sleep(1)

    def generate_invoice(self, order_id: str):
        logger.info(f"[BPMN] Generating invoice correlation_id={order_id}")
        time.sleep(1)

    def send_confirmation(self, order_id: str):
        db = SessionLocal()
        try:
            update_order_state(db, order_id, "COMPLETED", order_id)
            logger.info(f"[BPMN] Preparing confirmation correlation_id={order_id}")
            
            # Since workflow handles completion entirely, emit event here
            publish_message(EMAIL_NOTIFICATION_QUEUE, {
                "event": "ORDER_COMPLETED",
                "order_id": order_id,
                "correlation_id": order_id,
                "timestamp": datetime.utcnow().isoformat()
            }, correlation_id=order_id)
        finally:
            db.close()

workflow_worker = WorkflowWorker()
