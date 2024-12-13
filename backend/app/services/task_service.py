from sqlalchemy.orm import Session
from ..models.models import Task
from datetime import datetime

class TaskService:
    @staticmethod
    def create_task(db: Session, title: str, user_id: int = 1):
        task = Task(
            title=title,
            user_id=user_id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_tasks(db: Session, user_id: int = 1):
        return db.query(Task).filter(Task.user_id == user_id).all() 