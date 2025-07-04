import threading
import time
import requests
from services.task import Task
from utilities.logs import Logging


class Worker:
    def __init__(self, worker_id, scheduler_url):
        self.worker_id = worker_id
        self.scheduler_url = scheduler_url
        self.is_running = False
        self.current_task = None
        self.heartbeat_thread = None
        self.execution_thread = None
        self.logging = Logging()

    def _send_heartbeat(self):
        while self.is_running:
            try:
                requests.put(f"{self.scheduler_url}/heartbeat/{self.worker_id}")

            except requests.exceptions.ConnectionError:
                self.logging.info(f"Worker_id {self.worker_id}: Unable to connect to scheduler.")
            time.sleep(5)

    def _execute_task(self, task_data):
        available_functions = {
            "process_data": lambda x, y: x + y,
            "send_email": lambda recipient, subject, body: f"Email para {recipient}: {subject}",
            "calculate_pi": lambda n_digits: sum(1/16**k * (4/(8*k+1) - 2/(8*k+4) - 1/(8*k+5) - 1/(8*k+6)) for k in range(n_digits))
        }

        task = Task.from_dict(task_data, func_map=available_functions)
        self.current_task = task
        self.logging.info(f"Worker_id {self.worker_id}: Runing task_id {task.task_id} ({task.func.__name__})...")

        try:
            if task.func.__name__ not in available_functions:
                raise ValueError(f"Função '{task.func.__name__}' não encontrada no worker.")

            result = task.func(*task.args, **task.kwargs)
            requests.post(f"{self.scheduler_url}/task_status", json={
                "task_id": task.task_id,
                "status": "COMPLETED",
                "result": str(result),
                "worker_id": self.worker_id
            })
            self.logging.info(f"Worker_id {self.worker_id}: Task_id {task.task_id} COMPLET. Result: {result}")

        except Exception as e:
            requests.post(f"{self.scheduler_url}/task_status", json={
                "task_id": task.task_id,
                "status": "FAILED",
                "error_message": str(e),
                "worker_id": self.worker_id
            })
            self.logging.error(f"Worker_id {self.worker_id}: Task_id {task.task_id} FAILD. Error: {e}")
        finally:
            self.current_task = None


    def start(self):
        self.is_running = True
        self.logging.info(f"Worker_id {self.worker_id} running.")
        self.heartbeat_thread = threading.Thread(target=self._send_heartbeat, daemon=True)
        self.heartbeat_thread.start()

        while self.is_running:
            try:
                response = requests.get(f"{self.scheduler_url}/get_task/{self.worker_id}")
                if response.status_code == 200:
                    task_data = response.json()

                    if task_data:
                        self._execute_task(task_data)
                    else:
                        time.sleep(2)

                elif response.status_code == 204:
                    time.sleep(2)

                else:
                    self.logging.error(f"Worker_id {self.worker_id}: Error: {response.status_code} - {response.text}")
                    time.sleep(5)

            except requests.exceptions.ConnectionError:
                self.logging.warning(f"Worker_id {self.worker_id}: Connection to scheduler lost. Trying again...")
                time.sleep(5)

            except Exception as e:
                self.logging.error(f"Worker_id {self.worker_id}: Unexpected error in main loop: {e}")
                time.sleep(5)


    def stop(self):
        self.is_running = False
        self.logging.info(f"Worker_id {self.worker_id} stoped.")
        try:
            requests.delete(f"{self.scheduler_url}/unregister/{self.worker_id}")
        except requests.exceptions.ConnectionError:
            self.logging.info(f"Worker_id {self.worker_id}: Unable to unregister from scheduler.")
