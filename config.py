"""
Конфигурация приложения.
"""
import os
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
    pass


# Словарь доступных конфигураций
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)

# Текущая конфигурация
Config = config_by_name[os.environ.get('FLASK_ENV', 'development')] 