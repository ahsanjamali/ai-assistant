from openai import OpenAI
from datetime import datetime, timedelta
import os
import json
from sqlalchemy.orm import Session
from ..models.models import Task, Meeting
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta

class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = """You are a friendly AI assistant that helps manage tasks and meetings.
        
        For scheduling meetings, respond with:
        {"type": "action", "content": {"action": "schedule_meeting", "meeting": {"title": "Meeting with [name]", "date_info": "[extracted date/time]"}}}
        
        For tasks management:
        1. Adding tasks:
        {"type": "action", "content": {"action": "add_task", "task": "task description"}}
        
        2. Completing tasks:
        {"type": "action", "content": {"action": "complete_task", "task": "task description"}}
        
        3. Deleting tasks:
        {"type": "action", "content": {"action": "delete_task", "task": "task description"}}
        
        4. Viewing tasks:
        {"type": "action", "content": {"action": "get_tasks"}}
        
        For meetings management:
        1. Scheduling (with various date formats):
        - "tomorrow at 2pm"
        - "day after tomorrow at 3:30pm"
        - "next Monday at 10am"
        - "December 15 at 2pm"
        
        2. Viewing meetings:
        {"type": "action", "content": {"action": "get_meetings"}}
        
        3. Deleting meetings:
        {"type": "action", "content": {"action": "delete_meeting", "meeting": "meeting title"}}

        For general conversation or questions, respond with:
        {"type": "message", "content": "your helpful response"}

        Always maintain context and provide helpful responses."""

        # Add greeting patterns
        self.greetings = [
            "hi", "hello", "hey", "greetings", "good morning", 
            "good afternoon", "good evening", "howdy"
        ]
        self.thanks = [
            "thank", "thanks", "appreciate", "grateful", "thx", "great"
        ]

    def parse_date_info(self, date_info: str) -> datetime:
        try:
            now = datetime.now(pytz.UTC)
            
            # Handle relative dates
            lower_date = date_info.lower()
            if "tomorrow" in lower_date:
                base_date = now + timedelta(days=1)
            elif "day after tomorrow" in lower_date:
                base_date = now + timedelta(days=2)
            elif "next" in lower_date:
                # Handle "next Monday", "next week", etc.
                try:
                    base_date = parser.parse(date_info, fuzzy=True)
                except:
                    base_date = now + timedelta(weeks=1)
            else:
                # Parse absolute dates
                base_date = parser.parse(date_info, fuzzy=True)
            
            # If no time was specified, default to current time
            if base_date.hour == 0 and base_date.minute == 0:
                base_date = base_date.replace(
                    hour=now.hour,
                    minute=now.minute
                )
            
            return base_date

        except Exception as e:
            print(f"Date parsing error: {str(e)}")
            # Default to tomorrow at current time if parsing fails
            return now + timedelta(days=1)

    def get_tasks_text(self, db: Session) -> str:
        tasks = db.query(Task).all()
        if not tasks:
            return "You don't have any tasks at the moment."
        
        task_list = "\n".join([f"- {task.title} ({'completed' if task.completed else 'pending'})" for task in tasks])
        return f"Here are your tasks:\n{task_list}"

    def get_meetings_text(self, db: Session, date_filter=None) -> str:
        query = db.query(Meeting)
        
        if date_filter:
            # Filter meetings for specific date
            start_of_day = date_filter.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            query = query.filter(Meeting.start_time >= start_of_day, Meeting.start_time < end_of_day)
        
        meetings = query.order_by(Meeting.start_time).all()
        
        if not meetings:
            return f"You don't have any meetings{'tomorrow' if date_filter else ''}."
        
        meeting_list = "\n".join([
            f"- {meeting.title} at {meeting.start_time.strftime('%I:%M %p')}"
            for meeting in meetings
        ])
        
        date_str = "tomorrow" if date_filter else ""
        return f"Here are your meetings {date_str}:\n{meeting_list}"

    def complete_task(self, db: Session, task_description: str) -> str:
        # Find task by fuzzy matching the description
        task = db.query(Task).filter(
            Task.title.ilike(f"%{task_description}%")
        ).first()
        
        if task:
            task.completed = True
            db.commit()
            return f"✅ Marked task '{task.title}' as complete!"
        return f"❌ Couldn't find a task matching '{task_description}'"

    def delete_task(self, db: Session, task_description: str) -> str:
        task = db.query(Task).filter(
            Task.title.ilike(f"%{task_description}%")
        ).first()
        
        if task:
            db.delete(task)
            db.commit()
            return f"🗑️ Deleted task '{task.title}'"
        return f"❌ Couldn't find a task matching '{task_description}'"

    def delete_meeting(self, db: Session, meeting_title: str) -> str:
        meeting = db.query(Meeting).filter(
            Meeting.title.ilike(f"%{meeting_title}%")
        ).first()
        
        if meeting:
            db.delete(meeting)
            db.commit()
            return f"🗑️ Deleted meeting '{meeting.title}'"
        return f"❌ Couldn't find a meeting matching '{meeting_title}'"

    def is_greeting(self, message: str) -> bool:
        return any(greeting in message.lower() for greeting in self.greetings)

    def is_thanks(self, message: str) -> bool:
        return any(thank in message.lower() for thank in self.thanks)

    def process_message(self, message: str, db: Session) -> dict:
        # Handle greetings
        if self.is_greeting(message):
            return {
                "type": "message",
                "content": "Hello! I'm your AI assistant. I can help you manage tasks and schedule meetings. How can I help you today?"
            }
        
        # Handle thanks
        if self.is_thanks(message):
            return {
                "type": "message",
                "content": "You're welcome! Let me know if you need help with tasks or meetings."
            }

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            
            try:
                parsed_response = json.loads(assistant_message)
                
                if parsed_response["type"] == "action":
                    action = parsed_response["content"]["action"]
                    
                    # Handle meetings
                    if action == "schedule_meeting":
                        meeting_data = parsed_response["content"]["meeting"]
                        try:
                            meeting_time = self.parse_date_info(meeting_data["date_info"])
                            end_time = meeting_time + timedelta(hours=1)
                            return {
                                "type": "action",
                                "content": {
                                    "action": "schedule_meeting",
                                    "meeting": {
                                        "title": meeting_data["title"],
                                        "start_time": meeting_time.isoformat(),
                                        "end_time": end_time.isoformat()
                                    }
                                }
                            }
                        except Exception as e:
                            print(f"Meeting scheduling error: {str(e)}")
                            return {
                                "type": "message",
                                "content": "I had trouble with the date/time. Please try: 'tomorrow at 2pm' or 'December 15 at 14:00'"
                            }
                    
                    # Handle tasks
                    elif action == "add_task":
                        return parsed_response
                    elif action == "complete_task":
                        return {
                            "type": "message",
                            "content": self.complete_task(db, parsed_response["content"]["task"])
                        }
                    elif action == "delete_task":
                        return {
                            "type": "message",
                            "content": self.delete_task(db, parsed_response["content"]["task"])
                        }
                    elif action == "get_tasks":
                        return {
                            "type": "message",
                            "content": self.get_tasks_text(db)
                        }
                    
                    # Handle meeting queries/deletions
                    elif action == "get_meetings":
                        return {
                            "type": "message",
                            "content": self.get_meetings_text(db)
                        }
                    elif action == "delete_meeting":
                        return {
                            "type": "message",
                            "content": self.delete_meeting(db, parsed_response["content"]["meeting"])
                        }
                
                # For any other general questions
                if parsed_response["type"] == "message":
                    if not any(action_word in message.lower() for action_word in ["task", "meeting", "schedule"]):
                        return {
                            "type": "message",
                            "content": "I am a personal assistant focused on helping you manage tasks and meetings. Is there anything specific about tasks or meetings that I can help you with?"
                        }
                
                return parsed_response

            except json.JSONDecodeError:
                return {
                    "type": "message",
                    "content": "I'm a personal assistant focused on tasks and meetings. Could you please rephrase your request specifically about tasks or meetings?"
                }
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "type": "message",
                "content": "Sorry, I encountered an error. Please try again."
            } 