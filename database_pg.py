import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        invited_by BIGINT REFERENCES users(user_id),
        current_level INTEGER DEFAULT 1,
        total_points INTEGER DEFAULT 0
    )
    ''')
    
    # Таблица выполненных заданий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS completed_tasks (
        completion_id SERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(user_id),
        task_type VARCHAR(50) NOT NULL,
        completed_date DATE NOT NULL,
        proof_text TEXT,
        approved BOOLEAN DEFAULT FALSE
    )
    ''')
    
    # Таблица для книг
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        book_id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255),
        annotation TEXT,
        quote TEXT,
        external_link TEXT
    )
    ''')
    
    # Таблица для видео
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        video_id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        url TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # Таблица для продуктов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        benefits TEXT,
        testimonial TEXT
    )
    ''')
    
    # Вставляем базовые данные
    try:
        cursor.execute('''
        INSERT INTO books (title, author, annotation, quote, external_link) VALUES
            ('Думай и богатей', 'Наполеон Хилл', 'Классика о достижении успеха', 'Что разум человека может постигнуть и во что может поверить, того он способен и достичь.', ''),
            ('7 навыков высокоэффективных людей', 'Стивен Кови', 'Система развития личности', 'Начинайте, представляя конечную цель.', '')
        ON CONFLICT DO NOTHING
        ''')
        
        cursor.execute('''
        INSERT INTO videos (title, url, description) VALUES
            ('Сила мечты', 'https://youtube.com/watch?v=abc123', 'Вдохновляющее видео о постановке целей'),
            ('История успеха в Atomy', 'https://youtube.com/watch?v=def456', 'Реальная история достижений')
        ON CONFLICT DO NOTHING
        ''')
        
        cursor.execute('''
        INSERT INTO products (name, description, benefits, testimonial) VALUES
            ('HemoHIM', 'Иммунный усилитель', 'Укрепление иммунитета, повышение энергии', 'После месяца использования чувствую себя намного лучше!'),
            ('Absolute CellActive', 'Антивозрастной уход', 'Увлажнение, омоложение кожи', 'Кожа стала заметно свежее и моложе')
        ON CONFLICT DO NOTHING
        ''')
    except Exception as e:
        print(f"Ошибка при вставке базовых данных: {e}")
        conn.rollback()
    else:
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_db_structure():
    """Проверяет и обновляет структуру базы данных при необходимости"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем существование столбца task_type
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'completed_tasks' AND column_name = 'task_type'
        """)
        
        if not cursor.fetchone():
            # Добавляем столбец если он отсутствует
            cursor.execute("ALTER TABLE completed_tasks ADD COLUMN task_type VARCHAR(50)")
            print("Добавлен столбец task_type в таблицу completed_tasks")
        
        # Проверяем существование столбца external_link в books
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'books' AND column_name = 'external_link'
        """)
        
        if not cursor.fetchone():
            # Добавляем столбец если он отсутствует
            cursor.execute("ALTER TABLE books ADD COLUMN external_link TEXT")
            print("Добавлен столбец external_link в таблицу books")
        
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении структуры БД: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_user(user_id, username, full_name, invited_by=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, username, full_name, invited_by) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
            (user_id, username, full_name, invited_by)
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        cursor.close()
        conn.close()