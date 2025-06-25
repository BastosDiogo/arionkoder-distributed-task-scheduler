import heapq
import threading
import time
from services.task import Task
from datetime import datetime


class Scheduler:
    def __init__(self):
        self.task_queue = []
        self.all_tasks = {}
        self.pending_dependencies = {}
        self.workers = {}
        self.worker_heartbeats = {}

        self.lock = threading.Lock()

    def add_task(self, task: Task):
        with self.lock:
            self.all_tasks[task.task_id] = task
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id not in self.all_tasks or self.all_tasks[dep_id].status not in ["COMPLETED", "FAILED"]:
                        if task.task_id not in self.pending_dependencies:
                            self.pending_dependencies[task.task_id] = set()
                        self.pending_dependencies[task.task_id].add(dep_id)
            if not task.dependencies or not self.pending_dependencies.get(task.task_id):
               
                heapq.heappush(self.task_queue, (-task.priority, task.created_at, task.task_id))
                task.status = "PENDING"

    def _check_dependencies(self, task_id):
       
        if task_id not in self.all_tasks:
            return False
        task = self.all_tasks[task_id]
        if not task.dependencies:
            return True

        satisfied = True
        for dep_id in task.dependencies:
            if dep_id not in self.all_tasks or self.all_tasks[dep_id].status != "COMPLETED":
                satisfied = False
                break
        return satisfied

    def get_next_task(self, worker_id):
        with self.lock:
            if not self.task_queue:
                return None

            priority, _, task_id = heapq.heappop(self.task_queue)
            task = self.all_tasks[task_id]

            if not self._check_dependencies(task_id):
                heapq.heappush(self.task_queue, (priority, task.created_at, task.task_id))
                return None

            task.status = "RUNNING"
            task.started_at = datetime.now()
            task.worker_id = worker_id
            return task.to_dict()

    def update_task_status(self, task_id, status, result=None, error_message=None, worker_id=None):
        with self.lock:
            if task_id not in self.all_tasks:
                print(f"Erro: Tarefa {task_id} não encontrada.")
                return

            task = self.all_tasks[task_id]
            task.status = status
            task.worker_id = worker_id or task.worker_id

            if status == "COMPLETED":
                task.completed_at = datetime.now()

                for dependent_task_id, deps in list(self.pending_dependencies.items()):
                    if task_id in deps:
                        deps.remove(task_id)
                        if not deps:
                            del self.pending_dependencies[dependent_task_id]
                            dependent_task = self.all_tasks[dependent_task_id]
                            heapq.heappush(self.task_queue, (-dependent_task.priority, dependent_task.created_at, dependent_task.task_id))
                            dependent_task.status = "PENDING"
                print(f"Tarefa {task.task_id} COMPLETA por {task.worker_id}. Resultado: {result}")
            elif status == "FAILED":
                task.retries += 1
                if task.retries < task.max_retries:
                    task.status = "PENDING"
                    heapq.heappush(self.task_queue, (-task.priority, task.created_at, task.task_id))
                    print(f"Tarefa {task.task_id} FALHOU. Tentando novamente ({task.retries}/{task.max_retries}). Erro: {error_message}")
                else:
                    print(f"Tarefa {task.task_id} FALHOU definitivamente após {task.max_retries} tentativas. Erro: {error_message}")
            elif status == "CANCELED":
                print(f"Tarefa {task.task_id} CANCELADA.")
            elif status == "TIMED_OUT":
                task.retries += 1
                if task.retries < task.max_retries:
                    task.status = "PENDING"
                    heapq.heappush(self.task_queue, (-task.priority, task.created_at, task.task_id))
                    print(f"Tarefa {task.task_id} TEMPO LIMITE EXCEDIDO. Tentando novamente ({task.retries}/{task.max_retries}).")
                else:
                    print(f"Tarefa {task.task_id} TEMPO LIMITE EXCEDIDO definitivamente após {task.max_retries} tentativas.")

    def cancel_task(self, task_id):
        with self.lock:
            if task_id in self.all_tasks and self.all_tasks[task_id].status in ["PENDING", "RUNNING"]:
                self.all_tasks[task_id].status = "CANCELED"
               
                if self.all_tasks[task_id].status == "PENDING":
                    self.task_queue = [item for item in self.task_queue if item[2] != task_id]
                    heapq.heapify(self.task_queue)
                print(f"Requisição de cancelamento para a tarefa {task_id} enviada.")
               

    def register_worker(self, worker_id):
        with self.lock:
            self.workers[worker_id] = {"status": "ACTIVE", "last_heartbeat": time.time()}
            self.worker_heartbeats[worker_id] = time.time()
            print(f"Worker {worker_id} registrado.")

    def unregister_worker(self, worker_id):
        with self.lock:
            if worker_id in self.workers:
                del self.workers[worker_id]
                del self.worker_heartbeats[worker_id]
                print(f"Worker {worker_id} desregistrado.")
               
                for task_id, task in self.all_tasks.items():
                    if task.worker_id == worker_id and task.status == "RUNNING":
                        task.status = "PENDING"
                        heapq.heappush(self.task_queue, (-task.priority, task.created_at, task.task_id))
                        task.worker_id = None
                        print(f"Tarefa {task_id} do worker {worker_id} que falhou, re-enfileirada.")


    def worker_heartbeat(self, worker_id):
        with self.lock:
            if worker_id in self.workers:
                self.worker_heartbeats[worker_id] = time.time()
               

    def check_for_dead_workers(self, timeout_seconds=10):
       
        with self.lock:
            current_time = time.time()
            for worker_id, last_heartbeat in list(self.worker_heartbeats.items()):
                if current_time - last_heartbeat > timeout_seconds:
                    print(f"Worker {worker_id} inativo detectado! Removendo e re-enfileirando suas tarefas.")
                    self.unregister_worker(worker_id)

    def monitor_tasks_timeout(self):
        with self.lock:
            current_time = datetime.now()
            for task_id, task in self.all_tasks.items():
                if task.status == "RUNNING" and task.timeout is not None:
                    if (current_time - task.started_at).total_seconds() > task.timeout:
                        self.update_task_status(task_id, "TIMED_OUT", worker_id=task.worker_id)
                       
                        print(f"Tarefa {task_id} excedeu o tempo limite no worker {task.worker_id}.")

    def get_status_report(self):
        with self.lock:
            report = {
                "total_tasks": len(self.all_tasks),
                "tasks_by_status": {},
                "active_workers": len(self.workers),
                "worker_details": {wid: self.workers[wid] for wid in self.workers}
            }
            for task_id, task in self.all_tasks.items():
                report["tasks_by_status"].setdefault(task.status, 0)
                report["tasks_by_status"][task.status] += 1
            return report