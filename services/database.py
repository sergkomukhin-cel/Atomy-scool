from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models.base import Base
from models.user import User
from models.progress import UserProgress
from config import DATABASE_URL
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем движок и сессию
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    try:
        Base.metadata.create_all(engine)
        logger.info("База данных успешно инициализирована")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

def get_db_session():
    return Session()

def get_user(session, user_id):
    try:
        return session.query(User).filter(User.user_id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении пользователя {user_id}: {e}")
        return None

def create_user(session, user_id, username, first_name, last_name):
    try:
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        session.commit()
        logger.info(f"Создан новый пользователь: {user_id}")
        return user
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при создании пользователя {user_id}: {e}")
        return None

def update_user_progress(session, user_id, habit_type, notes=None):
    try:
        progress = UserProgress(
            user_id=user_id,
            habit_type=habit_type,
            notes=notes
        )
        session.add(progress)
        session.commit()
        logger.info(f"Обновлен прогресс пользователя {user_id} для привычки {habit_type}")
        return progress
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при обновлении прогресса пользователя {user_id}: {e}")
        return None

def update_user_quantum(session, user_id, amount):
    try:
        user = get_user(session, user_id)
        if user:
            user.quantum_balance += amount
            session.commit()
            logger.info(f"Обновлены кванты пользователя {user_id}: +{amount}")
            return user
        return None
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при обновлении квантов пользователя {user_id}: {e}")
        return None

def get_user_progress_stats(session, user_id, days=7):
    try:
        # Здесь будет логика получения статистики прогресса за указанное количество дней
        # Пока заглушка - реализуем после переноса основного функционала
        return {}
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении статистики пользователя {user_id}: {e}")
        return {}