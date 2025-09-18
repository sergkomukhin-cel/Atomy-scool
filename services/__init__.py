# Импортируем сервисы для удобного доступа
from .database import (
    get_db_session, get_user, create_user,
    update_user_progress, update_user_quantum,
    get_user_progress_stats
)

__all__ = [
    'get_db_session', 'get_user', 'create_user',
    'update_user_progress', 'update_user_quantum',
    'get_user_progress_stats'
]