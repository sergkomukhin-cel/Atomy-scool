import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import database_pg

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def dashboard():
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем статистику для дашборда
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM completed_tasks WHERE completed_date = CURRENT_DATE")
        today_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        # Последние 5 пользователей
        cursor.execute("""
            SELECT user_id, username, full_name, registered_at, current_level 
            FROM users ORDER BY registered_at DESC LIMIT 5
        """)
        recent_users = cursor.fetchall()
        
        # Последние выполненные задания
        cursor.execute("""
            SELECT u.full_name, ct.task_type, ct.completed_date 
            FROM completed_tasks ct
            JOIN users u ON ct.user_id = u.user_id
            ORDER BY ct.completed_date DESC LIMIT 10
        """)
        recent_tasks = cursor.fetchall()
        
    except Exception as e:
        flash(f'Ошибка при получении данных: {e}', 'error')
        return render_template('dashboard.html')
    finally:
        cursor.close()
        conn.close()
    
    return render_template('dashboard.html', 
                         total_users=total_users,
                         today_tasks=today_tasks,
                         total_books=total_books,
                         total_videos=total_videos,
                         total_products=total_products,
                         recent_users=recent_users,
                         recent_tasks=recent_tasks)

@app.route('/books')
def books():
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM books ORDER BY book_id")
        books = cursor.fetchall()
    except Exception as e:
        flash(f'Ошибка при получении списка книг: {e}', 'error')
        return render_template('books.html', books=[])
    finally:
        cursor.close()
        conn.close()
    
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    annotation = request.form.get('annotation')
    quote = request.form.get('quote')
    external_link = request.form.get('external_link')
    
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO books (title, author, annotation, quote, external_link) VALUES (%s, %s, %s, %s, %s)",
            (title, author, annotation, quote, external_link)
        )
        conn.commit()
        flash('Книга успешно добавлена!', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении книги: {e}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('books'))

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        annotation = request.form.get('annotation')
        quote = request.form.get('quote')
        external_link = request.form.get('external_link')
        
        try:
            cursor.execute(
                "UPDATE books SET title = %s, author = %s, annotation = %s, quote = %s, external_link = %s WHERE book_id = %s",
                (title, author, annotation, quote, external_link, book_id)
            )
            conn.commit()
            flash('Книга успешно обновлена!', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении книги: {e}', 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('books'))
    
    else:
        try:
            cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                flash('Книга не найдена!', 'error')
                return redirect(url_for('books'))
                
            return render_template('edit_book.html', book=book)
        except Exception as e:
            flash(f'Ошибка при получении данных книги: {e}', 'error')
            return redirect(url_for('books'))
        finally:
            cursor.close()
            conn.close()

@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        conn.commit()
        flash('Книга успешно удалена!', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении книги: {e}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('books'))

@app.route('/videos')
def videos():
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM videos ORDER BY video_id")
        videos = cursor.fetchall()
    except Exception as e:
        flash(f'Ошибка при получении списка видео: {e}', 'error')
        return render_template('videos.html', videos=[])
    finally:
        cursor.close()
        conn.close()
    
    return render_template('videos.html', videos=videos)

@app.route('/videos/add', methods=['POST'])
def add_video():
    title = request.form.get('title')
    url = request.form.get('url')
    description = request.form.get('description')
    
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO videos (title, url, description) VALUES (%s, %s, %s)",
            (title, url, description)
        )
        conn.commit()
        flash('Видео успешно добавлено!', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении видео: {e}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('videos'))

@app.route('/videos/edit/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        description = request.form.get('description')
        
        try:
            cursor.execute(
                "UPDATE videos SET title = %s, url = %s, description = %s WHERE video_id = %s",
                (title, url, description, video_id)
            )
            conn.commit()
            flash('Видео успешно обновлено!', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении видео: {e}', 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('videos'))
    
    else:
        try:
            cursor.execute("SELECT * FROM videos WHERE video_id = %s", (video_id,))
            video = cursor.fetchone()
            
            if not video:
                flash('Видео не найдено!', 'error')
                return redirect(url_for('videos'))
                
            return render_template('edit_video.html', video=video)
        except Exception as e:
            flash(f'Ошибка при получении данных видео: {e}', 'error')
            return redirect(url_for('videos'))
        finally:
            cursor.close()
            conn.close()

@app.route('/videos/delete/<int:video_id>')
def delete_video(video_id):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM videos WHERE video_id = %s", (video_id,))
        conn.commit()
        flash('Видео успешно удалено!', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении видео: {e}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('videos'))

@app.route('/products')
def products():
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM products ORDER BY product_id")
        products = cursor.fetchall()
    except Exception as e:
        flash(f'Ошибка при получении списка продуктов: {e}', 'error')
        return render_template('products.html', products=[])
    finally:
        cursor.close()
        conn.close()
    
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    description = request.form.get('description')
    benefits = request.form.get('benefits')
    testimonial = request.form.get('testimonial')
    
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO products (name, description, benefits, testimonial) VALUES (%s, %s, %s, %s)",
            (name, description, benefits, testimonial)
        )
        conn.commit()
        flash('Продукт успешно добавлен!', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении продукта: {e}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('products'))

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        benefits = request.form.get('benefits')
        testimonial = request.form.get('testimonial')
        
        try:
            cursor.execute(
                "UPDATE products SET name = %s, description = %s, benefits = %s, testimonial = %s WHERE product_id = %s",
                (name, description, benefits, testimonial, product_id)
            )
            conn.commit()
            flash('Продукт успешно обновлен!', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении продукта: {e}', 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('products'))
    
    else:
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                flash('Продукт не найден!', 'error')
                return redirect(url_for('products'))
                
            return render_template('edit_product.html', product=product)
        except Exception as e:
            flash(f'Ошибка при получении данных продукта: {e}', 'error')
            return redirect(url_for('products'))
        finally:
            cursor.close()
            conn.close()

@app.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        flash('Продукт успешно удален!', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении продукта: {e}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('products'))

@app.route('/users')
def users():
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT u.user_id, u.username, u.full_name, u.registered_at, 
                   u.current_level, u.total_points, COUNT(r.user_id) as referrals
            FROM users u
            LEFT JOIN users r ON u.user_id = r.invited_by
            GROUP BY u.user_id
            ORDER BY u.registered_at DESC
        """)
        users = cursor.fetchall()
    except Exception as e:
        flash(f'Ошибка при получении списка пользователей: {e}', 'error')
        return render_template('users.html', users=[])
    finally:
        cursor.close()
        conn.close()
    
    return render_template('users.html', users=users)

@app.route('/stats')
def stats():
    conn = database_pg.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Общая статистика
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM completed_tasks")
        total_completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        # Статистика по уровням
        cursor.execute("SELECT current_level, COUNT(*) FROM users GROUP BY current_level ORDER BY current_level")
        levels = cursor.fetchall()
        
        # Еженедельная активность (задачи по дням)
        cursor.execute("""
            SELECT completed_date, COUNT(*) 
            FROM completed_tasks 
            WHERE completed_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY completed_date 
            ORDER BY completed_date
        """)
        weekly_activity = cursor.fetchall()
        
    except Exception as e:
        flash(f'Ошибка при получении статистики: {e}', 'error')
        return render_template('stats.html')
    finally:
        cursor.close()
        conn.close()
    
    return render_template('stats.html', 
                         total_users=total_users,
                         total_completed_tasks=total_completed_tasks,
                         total_books=total_books,
                         total_videos=total_videos,
                         total_products=total_products,
                         levels=levels,
                         weekly_activity=weekly_activity)

if __name__ == '__main__':
    database_pg.init_db()
    database_pg.update_db_structure()
    app.run(debug=True, host='0.0.0.0', port=5000)