"""
Конфигурация приложения.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Базовый класс конфигурации приложения.
    """
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'секретный-ключ-по-умолчанию'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'university.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки для пагинации и других параметров
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """
    Конфигурация для разработки.
    """
    DEBUG = True


class TestingConfig(Config):
    """
    Конфигурация для тестирования.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Конфигурация для продакшена.
    """
    DEBUG = False
    
    # Рекомендуемые настройки для продакшена
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Специфичные настройки для базы данных в продакшн
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 299,
        'pool_timeout': 20,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    @classmethod
    def init_app(cls, app):
        """Инициализирует приложение с настройками для продакшена."""
        # Настройка логирования
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/university_portal.log',
            maxBytes=1024 * 1024 * 100,
            backupCount=10
        )
        file_format = (
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(logging.Formatter(file_format))
        file_handler.setLevel(logging.INFO)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Университетский портал запущен')


# Словарь доступных конфигураций
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)

# Текущая конфигурация
Config = config_by_name[os.environ.get('FLASK_ENV', 'development')] 