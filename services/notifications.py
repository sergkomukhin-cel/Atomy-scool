from telegram import Bot
from config import BOT_TOKEN
from services.database import get_db_session, get_user
import logging
from datetime import datetime, time
import asyncio

logger = logging.getLogger(__name__)

async def send_daily_reminder(user_id, message):
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=user_id, text=message)
        logger.info(f"Напоминание отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")

async def schedule_daily_reminders():
    while True:
        now = datetime.now().time()
        target_time = time(8, 0)  # 8:00 утра
        
        if now.hour == target_time.hour and now.minute == target_time.minute:
            session = get_db_session()
            try:
                # Здесь будет логика получения всех пользователей, которым нужно отправить напоминания
                # Пока заглушка - отправим себе для теста
                test_user_id = 123456789  # Замените на ваш user_id
                message = "Доброе утро! Не забудьте отметить свои привычки в трекере сегодня!"
                await send_daily_reminder(test_user_id, message)
                
                # Ждем 60 секунд, чтобы не отправлять несколько раз в одну минуту
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Ошибка при планировании напоминаний: {e}")
            finally:
                session.close()
        
        # Проверяем время каждую минуту
        await asyncio.sleep(60)