# Импортируем модели для удобного доступа
from .user import User
from .progress import UserProgress

__all__ = [
    'User',
    'UserProgress'
]