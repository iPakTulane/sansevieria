import os
import requests
import logging

logger = logging.getLogger("CAMUNDA_CLIENT")

class CamundaClient:
    def __init__(self):
        self.base_url = os.getenv("CAMUNDA_REST_URL", "http://localhost:8080/engine-rest")
        
    def start_process_instance(self, process_key: str, business_key: str, variables: dict = None):
        """Starts a process instance by key from Camunda with a business key correlation"""
        url = f"{self.base_url}/process-definition/key/{process_key}/start"
        payload = {
            "businessKey": business_key,
            "variables": self._format_variables(variables or {})
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"[CAMUNDA] Started process {process_key} for business_key={business_key}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[CAMUNDA] Failed to start process: {e}")
            return None

    def fetch_and_lock(self, worker_id: str, topic_name: str, lock_duration: int = 10000, max_tasks: int = 10):
        url = f"{self.base_url}/external-task/fetchAndLock"
        payload = {
            "workerId": worker_id,
            "maxTasks": max_tasks,
            "usePriority": True,
            "topics": [
                {
                    "topicName": topic_name,
                    "lockDuration": lock_duration,
                    "variables": ["order_id"]
                }
            ]
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def complete_task(self, task_id: str, worker_id: str, variables: dict = None):
        url = f"{self.base_url}/external-task/{task_id}/complete"
        payload = {
            "workerId": worker_id,
            "variables": self._format_variables(variables or {})
        }
        try:
            requests.post(url, json=payload, timeout=5).raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"[CAMUNDA] Failed to complete task {task_id}: {e}")
            return False

    def _format_variables(self, variables: dict):
        formatted = {}
        for k, v in variables.items():
            formatted[k] = {"value": v, "type": "String" if isinstance(v, str) else "Integer" if isinstance(v, int) else "Object"}
        return formatted

camunda_client = CamundaClient()
