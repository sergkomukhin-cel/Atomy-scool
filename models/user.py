from .base import Base  # Используем относительный импорт
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    level = Column(String, default='ИОН')
    quantum_balance = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, level={self.level})>"