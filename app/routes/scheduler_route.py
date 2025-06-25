from fastapi import APIRouter, status
from fastapi import HTTPException, status
from services.task import Task
from utilities.utilities_functions import get_func_from_name
from models.task_model import TaskCreate, TaskStatusUpdate
from services.scheduler import Scheduler

scheduler = Scheduler()
router = APIRouter(tags=["Scheduler"], prefix="/scheduler")


@router.post("/add_task", status_code=status.HTTP_201_CREATED)
async def add_task_endpoint(task_data: TaskCreate):
    """
    Adds a new task to the system.
    \nParameters:
    \n`func_name`: Function will be run. Format `str`
    \n`args`: Args (Optional). Format `list`;
    \n`kwargs`: Kwargs (Optional). Format `list`;
    \n`priority`: Priority task. Format `int`;
    \n`dependencies`: Kwargs (Optional). Format `list`.
    """
    func_to_execute = get_func_from_name(task_data.func_name)
    if not func_to_execute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Função '{task_data.func_name}' não reconhecida."
        )

    new_task = Task(
        func=func_to_execute,
        args=task_data.args,
        kwargs=task_data.kwargs,
        priority=task_data.priority,
        dependencies=task_data.dependencies,
        timeout=task_data.timeout
    )
    scheduler.add_task(new_task)
    return {"message": "Task add sucessful", "task_id": new_task.task_id}


@router.get("/get_task/{worker_id}")
async def get_task_endpoint(worker_id: str):
    """
    Allows a worker to request the next available task.
    """
    task_data = scheduler.get_next_task(worker_id)
    if task_data:
        return task_data
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Nenhuma tarefa disponível.")


@router.post("/task_status")
async def update_task_status_endpoint(update_data: TaskStatusUpdate):
    """
    Updates the status of a task.
    \nParameters:
    \n`task_id`: Task id. Format `str`
    \n`status`: Task status. Values (COMPLETED, FAILED, etc.). Format `str`;
    \n`worker_id`: Worker id. Format `str`.
    """
    scheduler.update_task_status(
        update_data.task_id,
        update_data.status,
        update_data.result,
        update_data.error_message,
        update_data.worker_id
    )
    return {"message": "Status da tarefa atualizado"}


@router.post("/cancel_task/{task_id}")
async def cancel_task_endpoint(task_id: str):
    """
    Requests the cancellation of a task.
    """
    scheduler.cancel_task(task_id)
    return {"message": f"Requisição de cancelamento para tarefa {task_id} enviada."}


@router.post("/register_worker/{worker_id}")
async def register_worker_endpoint(worker_id: str):
    """
    Registers a new worker with the scheduler.
    """
    scheduler.register_worker(worker_id)
    return {"message": f"Worker {worker_id} registrado."}


@router.delete("/unregister_worker/{worker_id}")
async def unregister_worker_endpoint(worker_id: str):
    """
    Unregisters a worker from the scheduler.
    """
    scheduler.unregister_worker(worker_id)
    return {"message": f"Worker {worker_id} desregistrado."}


@router.put("/heartbeat/{worker_id}")
async def heartbeat_endpoint(worker_id: str):
    """
    Receives a worker’s heartbeat to indicate it is active.
    """
    scheduler.worker_heartbeat(worker_id)
    return {"message": f"Heartbeat de {worker_id} recebido."}


@router.get("/status")
async def get_system_status():
    """
    Returns a full report of the system status.
    """
    report = scheduler.get_status_report()
    return report