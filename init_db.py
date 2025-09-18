# init_db.py
import database_pg

if __name__ == "__main__":
    print("Создание таблиц в базе данных...")
    database_pg.init_db()
    print("Обновление структуры базы данных...")
    database_pg.update_db_structure()
    print("Таблицы успешно созданы и обновлены!")