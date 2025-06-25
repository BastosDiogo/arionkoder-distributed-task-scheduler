from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class TaskCreate(BaseModel):
    """Class model to create a task requests."""
    func_name: str
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}
    priority: int = 0
    dependencies: Optional[List[str]] = []
    timeout: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    """Class model to update taks requests."""
    task_id: str
    status: str
    result: Optional[Any] = None
    error_message: Optional[str] = None
    worker_id: Optional[str] = None