from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from services.database import get_db_session, get_user, create_user, update_user_progress, update_user_quantum
from config import QUANTUMS_FOR_HABITS
import logging

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAITING_READING_CONFIRMATION, AWAITING_VIDEO_CONFIRMATION, AWAITING_PRODUCT_CONFIRMATION, AWAITING_MEETING_CONFIRMATION, AWAITING_CALL_CONFIRMATION = range(5)

async def handle_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда для запуска трекера"""
    await update.message.reply_text(
        "📋 Выберите привычку для отметки:\n\n"
        "📖 Чтение (15-30 мин)\n"
        "🎥 Просмотр видео\n"
        "🧴 Использование продукта\n"
        "🤝 Посещение встреч\n"
        "📞 Звонки/встречи",
        reply_markup=ReplyKeyboardMarkup([
            ["📖 Чтение", "🎥 Видео"],
            ["🧴 Продукт", "🤝 Встречи"],
            ["📞 Звонки"]
        ], one_time_keyboard=True)
    )

async def handle_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if not user:
            user = create_user(session, user_id, update.effective_user.username, 
                              update.effective_user.first_name, update.effective_user.last_name)
        
        # Здесь будет логика получения случайной книги из базы данных
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

async def handle_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if not user:
            user = create_user(session, user_id, update.effective_user.username, 
                              update.effective_user.first_name, update.effective_user.last_name)
        
        # Здесь будет логика получения случайного продукта из базы данных
        product_name = "Atomy HemoHIM"
        product_description = "Повышает иммунитет и улучшает общее состояние здоровья"
        
        await update.message.reply_text(
            f"🧴 Сегодня рекомендую попробовать: {product_name}\n\n"
            f"{product_description}\n\n"
            f"Использовал продукт сегодня?",
            reply_markup=ReplyKeyboardMarkup([["✅ Подтвердить использование"]], one_time_keyboard=True)
        )
        
        return AWAITING_PRODUCT_CONFIRMATION
        
    except Exception as e:
        logger.error(f"Ошибка в handle_product: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_product_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        
        # Обновляем прогресс пользователя
        update_user_progress(session, user_id, 'product')
        
        # Начисляем кванты
        update_user_quantum(session, user_id, QUANTUMS_FOR_HABITS['product'])
        
        await update.message.reply_text(
            f"Отлично! +{QUANTUMS_FOR_HABITS['product']} квантов начислено.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_product_confirmation: {e}")
        await update.message.reply_text("Произошла ошибка при подтверждении использования продукта.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if not user:
            user = create_user(session, user_id, update.effective_user.username, 
                              update.effective_user.first_name, update.effective_user.last_name)
        
        # Здесь будет логика получения информации о встречах
        await update.message.reply_text(
            "🤝 Посещение встреч и семинаров\n\n"
            "Какое мероприятие вы посетили сегодня?",
            reply_markup=ReplyKeyboardMarkup([["✅ Подтвердить посещение"]], one_time_keyboard=True)
        )
        
        return AWAITING_MEETING_CONFIRMATION
        
    except Exception as e:
        logger.error(f"Ошибка в handle_meeting: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_meeting_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        
        # Обновляем прогресс пользователя
        update_user_progress(session, user_id, 'meeting')
        
        # Начисляем кванты
        update_user_quantum(session, user_id, QUANTUMS_FOR_HABITS['meeting'])
        
        await update.message.reply_text(
            f"Отлично! +{QUANTUMS_FOR_HABITS['meeting']} квантов начислено.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_meeting_confirmation: {e}")
        await update.message.reply_text("Произошла ошибка при подтверждении посещения встречи.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        user = get_user(session, user_id)
        
        if not user:
            user = create_user(session, user_id, update.effective_user.username, 
                              update.effective_user.first_name, update.effective_user.last_name)
        
        # Здесь будет логика работы со звонками
        await update.message.reply_text(
            "📞 Звонки и встречи с людьми\n\n"
            "С кем вы пообщались сегодня?",
            reply_markup=ReplyKeyboardMarkup([["✅ Подтвердить звонок"]], one_time_keyboard=True)
        )
        
        return AWAITING_CALL_CONFIRMATION
        
    except Exception as e:
        logger.error(f"Ошибка в handle_call: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        return ConversationHandler.END
    finally:
        session.close()

async def handle_call_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    try:
        user_id = update.effective_user.id
        
        # Обновляем прогресс пользователя
        update_user_progress(session, user_id, 'call')
        
        # Начисляем кванты
        update_user_quantum(session, user_id, QUANTUMS_FOR_HABITS['call'])
        
        await update.message.reply_text(
            f"Отлично! +{QUANTUMS_FOR_HABITS['call']} квантов начислено.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_call_confirmation: {e}")
        await update.message.reply_text("Произошла ошибка при подтверждении звонка.")
        return ConversationHandler.END
    finally:
        session.close()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Операция отменена.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END