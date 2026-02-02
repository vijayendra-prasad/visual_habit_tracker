# models.py — placeholder for SQLAlchemy models
# Add `db = SQLAlchemy()` and model definitions here when needed.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database extension
# This object 'db' will be used to create tables and save data
db = SQLAlchemy()

class Habit(db.Model):
    """
    This table stores the name of the habit (e.g., 'Gym', 'Read').
    """
    id = db.Column(db.Integer, primary_key=True) # Unique ID for every habit
    name = db.Column(db.String(100), nullable=False) # The habit name
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # When you started it
    
    # Relationship: This links the Habit to its Daily Logs
    # It tells Flask: "One habit can have many logs"
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade="all, delete")

class HabitLog(db.Model):
    """
    This table stores every time you 'Check In' to a habit.
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False) # The day you did it
    
    # Advanced Feature: Mood tracking (1-10)
    # We add this now so your project stands out later!
    mood_score = db.Column(db.Integer, nullable=True) 
    
    # Foreign Key: This links this log to a specific Habit ID
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)