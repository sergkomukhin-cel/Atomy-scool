import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import DATABASE_URL
import logging
import pandas as pd
from sqlalchemy import create_engine
import json

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self, credentials_file='credentials.json'):
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
            self.client = gspread.authorize(creds)
            self.engine = create_engine(DATABASE_URL)
            logger.info("Google Sheets Manager инициализирован успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации Google Sheets Manager: {e}")
            raise

    def export_users_to_sheet(self, spreadsheet_name="Atomy Users"):
        try:
            # Получаем данные пользователей из базы данных
            query = "SELECT user_id, username, level, quantum_balance FROM users"
            df = pd.read_sql(query, self.engine)
            
            # Создаем или открываем таблицу
            try:
                spreadsheet = self.client.open(spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(spreadsheet_name)
            
            # Выбираем первый лист
            worksheet = spreadsheet.sheet1
            
            # Заголовки
            headers = ['User ID', 'Username', 'Level', 'Quantum Balance']
            worksheet.update([headers] + df.values.tolist())
            
            logger.info(f"Данные пользователей экспортированы в таблицу: {spreadsheet_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка экспорта данных в Google Sheets: {e}")
            return False

    def import_contacts_from_sheet(self, spreadsheet_url, user_id):
        try:
            # Открываем таблицу по URL
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.sheet1
            
            # Получаем все данные
            data = worksheet.get_all_values()
            
            if len(data) > 1:  # Если есть данные кроме заголовка
                # Здесь будет логика обработки контактов и сохранения в базу
                # Пока просто логируем
                logger.info(f"Импортировано {len(data)-1} контактов для пользователя {user_id}")
                return len(data) - 1
            return 0
        except Exception as e:
            logger.error(f"Ошибка импорта контактов из Google Sheets: {e}")
            return 0

# Создаем глобальный экземпляр для использования в других модулях
try:
    google_sheets_manager = GoogleSheetsManager()
except:
    google_sheets_manager = None
    logger.warning("Google Sheets Manager не инициализирован. Проверьте credentials.json")