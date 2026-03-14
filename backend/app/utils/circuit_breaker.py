import time
from app.utils.logger import get_logger

logger = get_logger("CIRCUIT_BREAKER")

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 15):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" 
    
    def call(self, func, correlation_id, order_id, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.cooldown_seconds:
                self.state = "HALF_OPEN"
                logger.info(correlation_id, order_id, "Circuit Breaker transitioned to HALF_OPEN")
            else:
                logger.error(correlation_id, order_id, "Circuit Breaker is OPEN. Call rejected.")
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
                logger.info(correlation_id, order_id, "Circuit Breaker transitioned to CLOSED")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(correlation_id, order_id, "Circuit Breaker transitioned to OPEN due to failures")
            raise e
