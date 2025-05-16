"""
Инициализация приложения Flask с использованием паттерна Application Factory.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Создаёт экземпляр приложения Flask с заданной конфигурацией.
    
    Args:
        config_class: Класс конфигурации для приложения
        
    Returns:
        flask.Flask: Экземпляр приложения Flask
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений с приложением
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    
    from app.routes.groups import bp as groups_bp
    app.register_blueprint(groups_bp, url_prefix='/groups')
    
    from app.routes.students import bp as students_bp
    app.register_blueprint(students_bp, url_prefix='/students')
    
    from app.routes.subjects import bp as subjects_bp
    app.register_blueprint(subjects_bp, url_prefix='/subjects')
    
    from app.routes.lessons import bp as lessons_bp
    app.register_blueprint(lessons_bp, url_prefix='/lessons')
    
    from app.routes.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    
    # Регистрация моделей (для Flask-Migrate)
    from app.models import user, group, student, subject, lesson, attendance
    
    @app.context_processor
    def utility_processor():
        """
        Определяет глобальные переменные для всех шаблонов.
        """
        from datetime import datetime
        from app.utils.helpers import format_date, calculate_attendance_percentage
        
        return dict(
            now=datetime.now(),
            format_date=format_date,
            calculate_attendance_percentage=calculate_attendance_percentage
        )
    
    return app 