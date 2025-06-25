import uuid
from datetime import datetime

class Task:
    def __init__(
        self,
        func,
        args=None,
        kwargs=None,
        priority=0,
        dependencies=None,
        timeout=None,
        max_retries=3
    ):
        """Class would represent the unit of work that your system needs to execute."""
        self.task_id = str(uuid.uuid4())
        self.func = func
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.priority = priority
        self.dependencies = dependencies if dependencies is not None else []
        self.status = "PENDING"
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.worker_id = None
        self.timeout = timeout
        self.retries = 0
        self.max_retries = max_retries

    def to_dict(self):
        """Method to serialize the task."""
        return {
            "task_id": self.task_id,
            "func": self.func.__name__ if hasattr(self.func, '__name__') else str(self.func),
            "args": self.args,
            "kwargs": self.kwargs,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "worker_id": self.worker_id,
            "timeout": self.timeout,
            "retries": self.retries,
            "max_retries": self.max_retries,
        }

    @staticmethod
    def from_dict(data, func_map=None):
        """Method to deserialize the task"""
        task = Task(
            func=func_map.get(data["func"], data["func"]) if func_map else data["func"],
            args=data.get("args"),
            kwargs=data.get("kwargs"),
            priority=data.get("priority", 0),
            dependencies=data.get("dependencies"),
            timeout=data.get("timeout")
        )

        task.task_id = data["task_id"]
        task.status = data["status"]
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.started_at = datetime.fromisoformat(data["started_at"]) if data["started_at"] else None
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None
        task.worker_id = data["worker_id"]
        task.retries = data.get("retries", 0)
        task.max_retries = data.get("max_retries", 3)
        return task