import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
from services.database import init_db
from handlers import (
    handle_reading, handle_reading_confirmation,
    handle_video, handle_video_confirmation,
    handle_product, handle_meeting, handle_call,
    handle_steps, handle_education, handle_mentor, handle_team_progress,
    AWAITING_READING_CONFIRMATION, AWAITING_VIDEO_CONFIRMATION,
    AWAITING_PRODUCT_CONFIRMATION, AWAITING_MEETING_CONFIRMATION,
    AWAITING_CALL_CONFIRMATION
)
from services.notifications import schedule_daily_reminders

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text(
        'Привет! Я бот системы "Путь мастера Atomy".\n\n'
        'Я помогу тебе отслеживать твой прогресс и развивать привычки успешного лидера.\n\n'
        'Доступные команды:\n'
        '/start - начать работу\n'
        '/tracker - открыть трекер привычек\n'
        '/steps - система 8 шагов\n'
        '/education - обучающие материалы\n'
        '/mentor - панель наставника\n'
        '/progress - мой прогресс'
    )

async def handle_progress(update, context):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if user:
            # Получаем статистику прогресса
            stats = get_user_progress_stats(session, user_id)
            
            await update.message.reply_text(
                f"📊 Твой прогресс:\n\n"
                f"Уровень: {user.level}\n"
                f"Квантов: {user.quantum_balance}\n"
                f"Привычек выполнено: {stats.get('total_habits', 0)}\n"
                f"Текущая серия: {stats.get('current_streak', 0)} дней"
            )
        else:
            await update.message.reply_text("Сначала зарегистрируйся с помощью /start")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_progress: {e}")
        await update.message.reply_text("Произошла ошибка при получении прогресса.")
    finally:
        session.close()

async def cancel(update, context):
    await update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def main():
    # Инициализация базы данных
    init_db()
    
    # Создаем приложение
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Обработчик команды /start
    application.add_handler(CommandHandler('start', start))
    
    # Обработчик команды /progress
    application.add_handler(CommandHandler('progress', handle_progress))
    
    # Обработчик трекера привычек с использованием ConversationHandler
    tracker_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('tracker', handle_reading)],
        states={
            AWAITING_READING_CONFIRMATION: [
                MessageHandler(filters.TEXT & filters.Regex('^✅ Подтвердить чтение$'), handle_reading_confirmation)
            ],
            AWAITING_VIDEO_CONFIRMATION: [
                MessageHandler(filters.TEXT & filters.Regex('^✅ Подтвердить просмотр$'), handle_video_confirmation)
            ],
            # Добавьте другие состояния для остальных привычек
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(tracker_conv_handler)
    
    # Обработчики для 8 шагов
    application.add_handler(CommandHandler('steps', handle_steps))
    
    # Обработчики для обучающих материалов
    application.add_handler(CommandHandler('education', handle_education))
    
    # Обработчики для наставников
    application.add_handler(CommandHandler('mentor', handle_mentor))
    application.add_handler(CommandHandler('team_progress', handle_team_progress))
    
    # Запускаем задачу для ежедневных напоминаний
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_daily_reminders())
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()