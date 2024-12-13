from sqlalchemy.orm import Session
from ..models.models import Meeting
from datetime import datetime

class MeetingService:
    @staticmethod
    def create_meeting(db: Session, title: str, start_time: datetime, end_time: datetime, user_id: int = 1):
        meeting = Meeting(
            title=title,
            start_time=start_time,
            end_time=end_time,
            user_id=user_id
        )
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        return meeting

    @staticmethod
    def get_meetings(db: Session, user_id: int = 1):
        return db.query(Meeting).filter(Meeting.user_id == user_id).all() 