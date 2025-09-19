from .base import Base  # Используем относительный импорт
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    habit_type = Column(String, nullable=False)
    completed = Column(Integer, default=1)
    notes = Column(String)
    date = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, habit_type={self.habit_type}, date={self.date})>"