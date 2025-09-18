from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def handle_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Здесь будет логика работы с 8 шагами GCMS
        await update.message.reply_text(
            "Система 8 шагов GCMS:\n\n"
            "1. Мечты и цели\n"
            "2. Решимость и целеустремленность\n"
            "3. Составление списка\n"
            "4. Встреча и приглашение\n"
            "5. Бизнес-план\n"
            "6. Контроль\n"
            "7. Консультирование\n"
            "8. Дублирование\n\n"
            "Выберите шаг для подробной информации."
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_steps: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")

async def handle_step_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, step_number: int):
    try:
        step_descriptions = {
            1: "Шаг 1: Мечты и цели - Определите яркие, конкретные мечты во всех сферах жизни.",
            2: "Шаг 2: Решимость - Дайте себе обещание достичь целей. Вырабатывайте привычки «Самолидерства».",
            # Добавьте остальные шаги
        }
        
        description = step_descriptions.get(step_number, "Шаг не найден.")
        await update.message.reply_text(description)
    except Exception as e:
        logger.error(f"Ошибка в handle_step_detail: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")