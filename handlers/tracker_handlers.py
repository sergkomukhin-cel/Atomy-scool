from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from services.database import get_db_session, get_user, create_user, update_user_progress, update_user_quantum
from config import QUANTUMS_FOR_HABITS
import logging

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAITING_READING_CONFIRMATION, AWAITING_VIDEO_CONFIRMATION, AWAITING_PRODUCT_CONFIRMATION, AWAITING_MEETING_CONFIRMATION, AWAITING_CALL_CONFIRMATION = range(5)

async def handle_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if not user:
            user = create_user(session, user_id, update.effective_user.username, 
                              update.effective_user.first_name, update.effective_user.last_name)
        
        # Здесь будет логика получения случайной книги из базы данных
        # Пока заглушка - реализуем после переноса основного функционала
        book_title = "Думай и богатей"
        book_quote = "Что разум человека может постигнуть и во что может поверить, того он способен и достичь."
        
        await update.message.reply_text(
            f"📖 Сегодня для роста рекомендую: {book_title}\n\n"
            f"{book_quote}\n\n"
            f"Прочитал 15-30 минут?",
            reply_markup=ReplyKeyboardMarkup([["✅ Подтвердить чтение"]], one_time_keyboard=True)
        )
        
        return AWAITING_READING_CONFIRMATION
        
    except Exception as e:
        logger.error(f"Ошибка в handle_reading: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_reading_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        
        # Обновляем прогресс пользователя
        update_user_progress(session, user_id, 'reading')
        
        # Начисляем кванты
        update_user_quantum(session, user_id, QUANTUMS_FOR_HABITS['reading'])
        
        await update.message.reply_text(
            f"Отлично! +{QUANTUMS_FOR_HABITS['reading']} квантов начислено.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_reading_confirmation: {e}")
        await update.message.reply_text("Произошла ошибка при подтверждении чтения.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if not user:
            user = create_user(session, user_id, update.effective_user.username, 
                              update.effective_user.first_name, update.effective_user.last_name)
        
        # Здесь будет логика получения случайного видео из базы данных
        video_title = "История успеха в Atomy"
        video_url = "https://youtube.com/watch?v=example"
        
        await update.message.reply_text(
            f"🎥 Сегодня для вдохновения: {video_title}\n\n"
            f"Ссылка: {video_url}\n\n"
            f"Посмотрел видео?",
            reply_markup=ReplyKeyboardMarkup([["✅ Подтвердить просмотр"]], one_time_keyboard=True)
        )
        
        return AWAITING_VIDEO_CONFIRMATION
        
    except Exception as e:
        logger.error(f"Ошибка в handle_video: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_video_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        
        # Обновляем прогресс пользователя
        update_user_progress(session, user_id, 'video')
        
        # Начисляем кванты
        update_user_quantum(session, user_id, QUANTUMS_FOR_HABITS['video'])
        
        await update.message.reply_text(
            f"Отлично! +{QUANTUMS_FOR_HABITS['video']} квантов начислено.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_video_confirmation: {e}")
        await update.message.reply_text("Произошла ошибка при подтверждении просмотра.")
        return ConversationHandler.END
    finally:
        session.close()

# Аналогично создайте обработчики для других привычек (product, meeting, call)
# Для экономии места покажу только заглушки

async def handle_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функционал для продуктов будет реализован позже.")
    return ConversationHandler.END

async def handle_meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функционал для встреч будет реализован позже.")
    return ConversationHandler.END

async def handle_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функционал для звонков будет реализован позже.")
    return ConversationHandler.END