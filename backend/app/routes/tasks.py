from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service = TaskService()

@router.get("")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = task_service.get_tasks(db)
    return {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "completed": task.completed
            } for task in tasks
        ]
    } 