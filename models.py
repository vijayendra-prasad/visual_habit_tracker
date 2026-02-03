# models.py — placeholder for SQLAlchemy models
# Add `db = SQLAlchemy()` and model definitions here when needed.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Initialize the database extension
# This object 'db' will be used to create tables and save data
db = SQLAlchemy()

def _now_utc():
    return datetime.now(timezone.utc)

class Habit(db.Model):
    """
    This table stores the name of the habit (e.g., 'Gym', 'Read').
    """
    id = db.Column(db.Integer, primary_key=True) # Unique ID for every habit
    name = db.Column(db.String(100), nullable=False) # The habit name
    created_at = db.Column(db.DateTime, default=_now_utc) # When you started it (timezone-aware)
    
    # Relationship: This links the Habit to its Daily Logs
    # It tells Flask: "One habit can have many logs"
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade="all, delete")

class HabitLog(db.Model):
    """
    This table stores every time you 'Check In' to a habit.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Keep a date-only column for legacy compatibility
    date = db.Column(db.Date, default=lambda: _now_utc().date(), nullable=False)

    # Timestamp for the exact time of the log (used for calendar/times)
    timestamp = db.Column(db.DateTime, default=_now_utc, nullable=False)

    # Advanced Feature: Mood tracking (1-10)
    mood_score = db.Column(db.Integer, nullable=True) 
    
    # Foreign Key: This links this log to a specific Habit ID
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)

    def __repr__(self):
        return f"<HabitLog {self.id} habit={self.habit_id} ts={self.timestamp}>"