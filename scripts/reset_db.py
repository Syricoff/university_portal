"""
Скрипт для сброса и пересоздания базы данных.
"""
from app import create_app, db

app = create_app()

def reset_database():
    """Сбрасывает базу данных и создает все таблицы заново."""
    with app.app_context():
        print("Удаление всех таблиц...")
        db.drop_all()
        print("Создание новых таблиц...")
        db.create_all()
        print("База данных успешно сброшена.")

if __name__ == "__main__":
    reset_database() 