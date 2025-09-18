import os
import random
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import database_pg
import asyncio

# Загружаем токен из файла .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Проверяем, что токен загружен
if not TOKEN:
    raise ValueError("Токен не найден! Проверьте файл .env")

# Функция-обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name
    
    # Пытаемся получить ID пригласившего из аргументов команды
    invited_by = None
    if context.args:
        try:
            invited_by = int(context.args[0])
            # Проверяем, существует ли пользователь, который пригласил
            conn = database_pg.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (invited_by,))
            if not cursor.fetchone():
                invited_by = None
            cursor.close()
            conn.close()
        except ValueError:
            invited_by = None
    
    # Регистрируем пользователя в БД PostgreSQL
    database_pg.add_user(user.id, user.username, user.full_name, invited_by)
    
    welcome_text = f"Привет, {user_name}! Добро пожаловать в систему обучения! Ты успешно зарегистрирован(а)."
    
    if invited_by:
        welcome_text += "\n\nСпасибо, что присоединились по приглашению!"
    
    welcome_text += "\n\nИспользуй /help для просмотра доступных команд."
    
    await update.message.reply_text(welcome_text)

# Функция-обработчик команды /profile
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Получаем информацию о пользователе из БД
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT u.*, COUNT(r.user_id) as referrals_count 
            FROM users u 
            LEFT JOIN users r ON u.user_id = r.invited_by 
            WHERE u.user_id = %s 
            GROUP BY u.user_id
        """, (user.id,))
        user_data = cursor.fetchone()
        
        if user_data:
            # Получаем информацию о пригласившем, если есть
            inviter_name = "Не указан"
            if user_data[4]:
                cursor.execute("SELECT full_name FROM users WHERE user_id = %s", (user_data[4],))
                inviter_data = cursor.fetchone()
                if inviter_data:
                    inviter_name = inviter_data[0]
            
            response = (
                f"👤 <b>Ваш профиль</b>\n\n"
                f"🆔 ID: {user_data[0]}\n"
                f"👤 Имя: {user_data[2]}\n"
                f"🎯 Уровень: {user_data[5]}\n"
                f"⭐ Очки: {user_data[6]}\n"
                f"👥 Пригласил: {inviter_name}\n"
                f"📊 Приглашенных: {user_data[7]}\n"
                f"📅 Дата регистрации: {user_data[3].strftime('%Y-%m-%d %H:%M')}\n\n"
                f"💡 Используйте /help для списка команд"
            )
        else:
            response = "❌ Ваш профиль не найден. Используйте /start для регистрации."
        
        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        print(f"Ошибка при получении профиля: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении данных профиля.")
    finally:
        cursor.close()
        conn.close()

# Функция-обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 <b>Доступные команды:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/profile - Посмотреть свой профиль\n"
        "/tracker - Открыть ежедневный трекер привычек\n"
        "/progress - Показать прогресс за неделю\n"
        "/help - Показать это сообщение\n\n"
        "⚡ <b>Скоро появится:</b>\n"
        "/invite - Пригласить друзей\n"
        "/tasks - Ежедневные задания\n"
        "/level - Информация об уровнях"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

# Функция-обработчик команды /tracker
async def tracker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_daily_tracker(context, user.id)

# Функция для отправки ежедневного трекера
async def send_daily_tracker(context: ContextTypes.DEFAULT_TYPE, user_id: int = None):
    if user_id is None:
        return
    
    # Получаем случайные материалы для дня
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем случайную книгу
        cursor.execute("SELECT * FROM books ORDER BY RANDOM() LIMIT 1")
        book = cursor.fetchone()
        
        # Получаем случайное видео
        cursor.execute("SELECT * FROM videos ORDER BY RANDOM() LIMIT 1")
        video = cursor.fetchone()
        
        # Получаем случайный продукт
        cursor.execute("SELECT * FROM products ORDER BY RANDOM() LIMIT 1")
        product = cursor.fetchone()
        
        # Отправляем раздельное сообщение для каждой привычки
        
        # 1. Сообщение о книге
        if book:
            book_title = book[1] or "Без названия"
            book_author = book[2] or "Неизвестный автор"
            short_quote = book[4][:100] + "..." if book[4] and len(book[4]) > 100 else book[4] or "Цитата не указана"
            
            book_message = (
                f"📖 <b>Чтение (15-30 мин)</b>\n\n"
                f"<b>Книга:</b> {book_title}\n"
                f"<b>Автор:</b> {book_author}\n"
                f"<b>Цитата:</b> {short_quote}\n\n"
                f"<i>Используйте кнопку ниже для полной цитаты</i>"
            )
            
            book_keyboard = [
                [InlineKeyboardButton("✅ Чтение выполнено", callback_data="habit_reading")],
                [InlineKeyboardButton("📖 Полная цитата", callback_data=f"full_quote_{book[0]}")]
            ]
            book_reply_markup = InlineKeyboardMarkup(book_keyboard)
            
            await context.bot.send_message(
                chat_id=user_id,
                text=book_message,
                reply_markup=book_reply_markup,
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="📖 <b>Чтение (15-30 мин)</b>\n\nНа сегодня книг нет в базе",
                parse_mode='HTML'
            )
        
        # 2. Сообщение о видео
        if video:
            video_title = video[1] or "Без названия"
            video_description = video[3] or "Описание отсутствует"
            
            video_message = (
                f"🎬 <b>Просмотр мотивирующих видео</b>\n\n"
                f"<b>Видео:</b> {video_title}\n"
                f"<b>Описание:</b> {video_description}\n"
                f"<b>Ссылка:</b> {video[2]}"
            )
            
            video_keyboard = [
                [InlineKeyboardButton("✅ Видео просмотрено", callback_data="habit_video")]
            ]
            video_reply_markup = InlineKeyboardMarkup(video_keyboard)
            
            await context.bot.send_message(
                chat_id=user_id,
                text=video_message,
                reply_markup=video_reply_markup,
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎬 <b>Просмотр мотивирующих видео</b>\n\nНа сегодня видео нет в базе",
                parse_mode='HTML'
            )
        
        # 3. Сообщение о продукте
        if product:
            product_name = product[1] or "Без названия"
            product_description = product[2] or "Описание отсутствует"
            product_benefits = product[3] or "Преимущества не указаны"
            
            product_message = (
                f"🧴 <b>Использование продуктов Atomy</b>\n\n"
                f"<b>Продукт:</b> {product_name}\n"
                f"<b>Описание:</b> {product_description}\n"
                f"<b>Преимущества:</b> {product_benefits}\n\n"
                f"<b>Отзыв:</b> {product[4] or 'Отзывов пока нет'}"
            )
            
            product_keyboard = [
                [InlineKeyboardButton("✅ Продукт использован", callback_data="habit_product")]
            ]
            product_reply_markup = InlineKeyboardMarkup(product_keyboard)
            
            await context.bot.send_message(
                chat_id=user_id,
                text=product_message,
                reply_markup=product_reply_markup,
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="🧴 <b>Использование продуктов Atomy</b>\n\nНа сегодня продуктов нет в базе",
                parse_mode='HTML'
            )
        
        # 4. Сообщение с остальными кнопками
        final_message = (
            f"📋 <b>Ежедневный трекер привычек</b>\n\n"
            f"Отметьте выполнение всех привычек:"
        )
        
        final_keyboard = [
            [InlineKeyboardButton("✅ Участие в мероприятии", callback_data="habit_event")],
            [InlineKeyboardButton("✅ Звонок/встреча", callback_data="habit_call")],
            [InlineKeyboardButton("📊 Показать прогресс", callback_data="show_progress")],
            [InlineKeyboardButton("❌ Закрыть трекер", callback_data="close_tracker")]
        ]
        final_reply_markup = InlineKeyboardMarkup(final_keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=final_message,
            reply_markup=final_reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        print(f"Ошибка при отправке трекера: {e}")
    finally:
        cursor.close()
        conn.close()

# Функция для отправки полной цитаты
async def send_full_quote(context: ContextTypes.DEFAULT_TYPE, user_id: int, book_id: int):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем полную информацию о книге
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        
        if book:
            book_title = book[1] or "Без названия"
            book_author = book[2] or "Неизвестный автор"
            full_quote = book[4] or "Цитата не указана"
            external_link = book[5]  # Внешняя ссылка
            
            if external_link:
                # Если есть внешняя ссылка, отправляем ее
                quote_message = (
                    f"📖 <b>Полная цитата из книги</b>\n\n"
                    f"<b>Книга:</b> {book_title}\n"
                    f"<b>Автор:</b> {book_author}\n\n"
                    f"Полная цитата доступна по ссылке:\n{external_link}"
                )
            elif len(full_quote) <= 4000:
                # Если цитата не слишком длинная, отправляем полностью
                quote_message = (
                    f"📖 <b>Полная цитата из книги</b>\n\n"
                    f"<b>Книга:</b> {book_title}\n"
                    f"<b>Автор:</b> {book_author}\n\n"
                    f"{full_quote}"
                )
            else:
                # Если цитата очень длинная, отправляем часть и предлагаем ссылку
                quote_message = (
                    f"📖 <b>Полная цитата из книги</b>\n\n"
                    f"<b>Книга:</b> {book_title}\n"
                    f"<b>Автор:</b> {book_author}\n\n"
                    f"Цитата слишком длинная для отображения в Telegram. "
                    f"Пожалуйста, добавьте внешнюю ссылку на полную версию в админ-панели."
                )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=quote_message,
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Книга не найдена."
            )
            
    except Exception as e:
        print(f"Ошибка при отправке полной цитаты: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Произошла ошибка при получении цитаты."
        )
    finally:
        cursor.close()
        conn.close()

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Обработка полной цитаты
    if data.startswith("full_quote_"):
        book_id = data.replace("full_quote_", "")
        await send_full_quote(context, user_id, book_id)
        return
    
    # Обрабатываем разные типы привычек
    if data.startswith("habit_"):
        habit_name = data.replace("habit_", "")
        
        # Сохраняем в базу данных
        conn = database_pg.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO completed_tasks (user_id, task_type, completed_date) VALUES (%s, %s, %s)",
                (user_id, habit_name, datetime.now().date())
            )
            conn.commit()
            
            # Отправляем подтверждение, но не изменяем исходное сообщение
            await context.bot.send_message(
                chat_id=user_id,
                text=f"✅ Привычка '{habit_name}' отмечена как выполненная!",
                reply_to_message_id=query.message.message_id
            )
            
        except Exception as e:
            print(f"Ошибка при сохранении привычки: {e}")
            await query.edit_message_text(
                text="❌ Произошла ошибка при сохранении. Попробуйте позже."
            )
        finally:
            cursor.close()
            conn.close()
    
    elif data == "show_progress":
        # Показываем прогресс
        await show_progress(query)
    
    elif data == "close_tracker":
        # Удаляем сообщение с трекером
        await query.delete_message()

# Функция для показа прогресса
async def show_progress(query):
    user_id = query.from_user.id
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем прогресс за последние 7 дней
        cursor.execute("""
            SELECT task_type, COUNT(*) 
            FROM completed_tasks 
            WHERE user_id = %s AND completed_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY task_type
        """, (user_id,))
        
        progress = cursor.fetchall()
        
        # Формируем сообщение о прогрессе
        message = "📊 <b>Ваш прогресс за неделю:</b>\n\n"
        
        habits = {
            'reading': '📖 Чтение',
            'video': '🎬 Видео',
            'product': '🧴 Продукты',
            'event': '📅 Мероприятия',
            'call': '📞 Звонки/встречи'
        }
        
        for habit_type, habit_name in habits.items():
            count = 0
            for p in progress:
                if p[0] == habit_type:
                    count = p[1]
                    break
            
            message += f"{habit_name}: {count}/7\n"
        
        message += "\nПродолжайте в том же духе! 💪"
        
        await query.edit_message_text(
            text=message,
            parse_mode='HTML'
        )
        
    except Exception as e:
        print(f"Ошибка при получении прогресса: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при получении прогресса."
        )
    finally:
        cursor.close()
        conn.close()

# Функция для команды /progress
async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Получаем прогресс за последние 7 дней
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT task_type, COUNT(*) 
            FROM completed_tasks 
            WHERE user_id = %s AND completed_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY task_type
        """, (user.id,))
        
        progress = cursor.fetchall()
        
        # Формируем сообщение о прогрессе
        message = "📊 <b>Ваш прогресс за неделю:</b>\n\n"
        
        habits = {
            'reading': '📖 Чтение',
            'video': '🎬 Видео',
            'product': '🧴 Продукты',
            'event': '📅 Мероприятия',
            'call': '📞 Звонки/встречи'
        }
        
        for habit_type, habit_name in habits.items():
            count = 0
            for p in progress:
                if p[0] == habit_type:
                    count = p[1]
                    break
            
            message += f"{habit_name}: {count}/7\n"
        
        message += "\nПродолжайте в том же духе! 💪"
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        print(f"Ошибка при получении прогресса: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении прогресса.")
    finally:
        cursor.close()
        conn.close()

# Функция для ежедневной рассылки трекера
async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    # Получаем всех пользователей
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("Нет пользователей для рассылки")
            return
            
        for user in users:
            await send_daily_tracker(context, user[0])
            await asyncio.sleep(0.1)  # Небольшая задержка между отправками
            
    except Exception as e:
        print(f"Ошибка при ежедневной рассылке: {e}")
    finally:
        cursor.close()
        conn.close()

# Главная функция
def main():
    # Инициализируем базу данных
    database_pg.init_db()
    database_pg.update_db_structure()
    
    # Создаем приложение и передаем ему токен
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tracker", tracker_command))
    app.add_handler(CommandHandler("progress", progress_command))
    
    # Добавляем обработчик кнопок
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Настраиваем ежедневную рассылку в 9:00
    job_queue = app.job_queue
    job_queue.run_daily(daily_reminder, time=time(hour=9, minute=0, second=0))
    
    # Запускаем бота на постоянную проверку новых сообщений
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()