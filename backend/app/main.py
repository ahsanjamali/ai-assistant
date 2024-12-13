from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .models.base import Base, engine, get_db
from .services.ai_service import AIAssistant
from .models.models import Task, Meeting
from datetime import datetime
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Ensure OpenAI API key is set
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
ai_assistant = AIAssistant()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(message: MessageRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received message: {message.message}")
        
        # Pass db session to process_message
        response = ai_assistant.process_message(message.message, db)
        logger.info(f"AI response: {response}")
        
        # Handle actions
        if response["type"] == "action":
            action_data = response["content"]
            logger.info(f"Processing action: {action_data}")
            
            if action_data["action"] == "add_task":
                # Create task in database
                task = Task(
                    title=action_data["task"]
                )
                db.add(task)
                db.commit()
                logger.info(f"Task created: {task.title}")
                return {"type": "message", "content": f"✅ Task added: {task.title}"}
                
            elif action_data["action"] == "schedule_meeting":
                # Create meeting in database
                meeting = Meeting(
                    title=action_data["meeting"]["title"],
                    start_time=datetime.fromisoformat(action_data["meeting"]["start_time"]),
                    end_time=datetime.fromisoformat(action_data["meeting"]["start_time"])
                )
                db.add(meeting)
                db.commit()
                logger.info(f"Meeting created: {meeting.title}")
                return {"type": "message", "content": f"📅 Meeting scheduled: {meeting.title}"}
        
        return response

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Add a test endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).order_by(Task.created_at.desc()).all()
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "created_at": task.created_at
                } for task in tasks
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

@app.get("/api/meetings")
async def get_meetings(db: Session = Depends(get_db)):
    try:
        meetings = db.query(Meeting).order_by(Meeting.start_time.asc()).all()
        return {
            "meetings": [
                {
                    "id": meeting.id,
                    "title": meeting.title,
                    "start_time": meeting.start_time,
                    "end_time": meeting.end_time
                } for meeting in meetings
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching meetings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch meetings")