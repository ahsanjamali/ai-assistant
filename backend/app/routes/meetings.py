from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..services.meeting_service import MeetingService

router = APIRouter(prefix="/meetings", tags=["meetings"])
meeting_service = MeetingService()

@router.get("")
async def get_meetings(db: Session = Depends(get_db)):
    meetings = meeting_service.get_meetings(db)
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