from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..services.ai_service import AIAssistant
from ..services.task_service import TaskService
from ..services.meeting_service import MeetingService
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

router = APIRouter()
ai_assistant = AIAssistant()
task_service = TaskService()
meeting_service = MeetingService()

class MessageRequest(BaseModel):
    message: str

@router.post("/chat")
async def process_message(message_request: MessageRequest, db: Session = Depends(get_db)):
    response = ai_assistant.process_message(message_request.message)
    print("AI Response:", response)  # Debug print
    
    if isinstance(response, dict) and response.get("type") == "action":
        action_data = response["content"]
        
        if action_data.get("action") == "add_task":
            # Get task title from the correct field
            task_title = action_data.get("task", "")
            print("Task title:", task_title)  # Debug print
            
            if task_title:
                task = task_service.create_task(
                    db=db,
                    title=task_title
                )
                return {
                    "type": "message",
                    "content": f"✅ Task added: {task.title}"
                }
    
    return response

@router.get("/tasks")
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

@router.get("/meetings")
async def get_meetings(db: Session = Depends(get_db)):
    meetings = meeting_service.get_meetings(db)
    return {"meetings": [
        {
            "id": meeting.id,
            "title": meeting.title,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time
        } for meeting in meetings
    ]} 