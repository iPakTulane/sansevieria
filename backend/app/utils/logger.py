import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def _log(self, level, correlation_id, order_id, message, **kwargs):
        extras = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        formatted = f"[{level}] service={self.service_name} correlation_id={correlation_id} order_id={order_id} message=\"{message}\" {extras}"
        if level == "ERROR":
            self.logger.error(formatted)
        elif level == "WARNING":
            self.logger.warning(formatted)
        else:
            self.logger.info(formatted)

    def info(self, correlation_id, order_id, message, **kwargs):
        self._log("INFO", correlation_id, order_id, message, **kwargs)

    def error(self, correlation_id, order_id, message, **kwargs):
        self._log("ERROR", correlation_id, order_id, message, **kwargs)

def get_logger(service_name: str):
    return StructuredLogger(service_name)
