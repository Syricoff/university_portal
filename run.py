"""
Скрипт для запуска Flask приложения.
"""
import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Настройки запуска для продакшена и разработки
    is_prod = os.environ.get('FLASK_ENV') == 'production'
    host = '0.0.0.0' if is_prod else '127.0.0.1'
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    app.run(host=host, port=port, debug=debug)