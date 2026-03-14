import time
import logging
import threading
from app.workflow.camunda_client import camunda_client
from app.database import SessionLocal
from app.services.order_state_service import update_order_state
from app.messaging.producer import publish_message
from app.messaging.queues import EMAIL_NOTIFICATION_QUEUE
from datetime import datetime
from app.utils.fault_handlers import with_retries, with_timeout
from app.utils.circuit_breaker import CircuitBreaker
from app.config import settings

logger = logging.getLogger("ORDER_PROCESSOR")
payment_circuit_breaker = CircuitBreaker(failure_threshold=3, cooldown_seconds=15)

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
                                handler(order_id, order_id) # pass correlation_id, order_id appropriately to fault handlers
                                camunda_client.complete_task(task["id"], self.worker_id)
                                logger.info(f"[BPMN] Completed task {topic} correlation_id={order_id}")
                            except Exception as e:
                                logger.error(f"[BPMN] Fatal Task error {topic} correlation_id={order_id}: {str(e)}")
                                # Transition to FAILED state since all retries have been exhausted
                                db = SessionLocal()
                                try:
                                    update_order_state(db, order_id, "FAILED", order_id)
                                except Exception:
                                    pass
                                finally:
                                    db.close()
                                # We deliberately do not complete_task on fatal errors to trigger Camunda incident tracking
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
    @with_retries(max_retries=3)
    def validate_order(self, correlation_id: str, order_id: str):
        db = SessionLocal()
        try:
            update_order_state(db, order_id, "PROCESSING", correlation_id)
            logger.info(f"[BPMN] Validated order correlation_id={correlation_id}")
        finally:
            db.close()

    @with_retries(max_retries=3)
    @with_timeout(seconds=5)
    def process_payment(self, correlation_id: str, order_id: str):
        def _mock_payment(corr_id, ord_id):
            logger.info(f"[BPMN] Processing payment correlation_id={corr_id}")
            if settings.SIMULATE_PAYMENT_FAILURE:
                time.sleep(1)
                raise Exception("Simulated Payment Gateway Timeout/Failure")
            time.sleep(1) # simulate external payment
            
        return payment_circuit_breaker.call(_mock_payment, correlation_id, order_id, correlation_id, order_id)

    @with_retries(max_retries=3)
    @with_timeout(seconds=5)
    def reserve_inventory(self, correlation_id: str, order_id: str):
        logger.info(f"[BPMN] Reserving inventory correlation_id={correlation_id}")
        time.sleep(1) # simulate inventory check

    @with_retries(max_retries=3)
    def generate_shipment(self, correlation_id: str, order_id: str):
        logger.info(f"[BPMN] Generating shipment correlation_id={correlation_id}")
        time.sleep(1)

    @with_retries(max_retries=3)
    def generate_invoice(self, correlation_id: str, order_id: str):
        logger.info(f"[BPMN] Generating invoice correlation_id={correlation_id}")
        time.sleep(1)

    @with_retries(max_retries=3)
    def send_confirmation(self, correlation_id: str, order_id: str):
        db = SessionLocal()
        try:
            update_order_state(db, order_id, "COMPLETED", correlation_id)
            logger.info(f"[BPMN] Preparing confirmation correlation_id={correlation_id}")
            publish_message(EMAIL_NOTIFICATION_QUEUE, {
                "event": "ORDER_COMPLETED",
                "order_id": order_id,
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat()
            }, correlation_id=correlation_id)
        finally:
            db.close()

workflow_worker = WorkflowWorker()
