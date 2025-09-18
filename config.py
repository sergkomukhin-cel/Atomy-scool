import os
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Настройки базы данных
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Настройки уровней пользователей
USER_LEVELS = {
    'ИОН': 1,
    'ФОТОН': 2,
    'ЭКСИТОН': 3,
    'КРИСТАЛЛ': 4
}

# Кванты за выполнение привычек
QUANTUMS_FOR_HABITS = {
    'reading': 10,
    'video': 8,
    'product': 7,
    'meeting': 12,
    'call': 15
}