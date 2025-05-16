"""
Модель пользователя системы.
"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    Модель пользователя системы.
    
    Attributes:
        id (int): Уникальный идентификатор пользователя
        username (str): Логин пользователя
        password (str): Хеш пароля пользователя
        role (str): Роль пользователя (student, admin, etc.)
        first_name (str): Имя пользователя
        last_name (str): Фамилия пользователя
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    # Связь с таблицей студентов (один-к-одному)
    student = db.relationship("Student", backref="user", uselist=False, cascade="all, delete-orphan")
    
    def __init__(self, username, password, role, first_name=None, last_name=None):
        """
        Инициализация пользователя.
        
        Args:
            username (str): Логин пользователя
            password (str): Пароль пользователя (будет хешироваться)
            role (str): Роль пользователя
            first_name (str, optional): Имя пользователя
            last_name (str, optional): Фамилия пользователя
        """
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
    
    def check_password(self, password):
        """
        Проверка пароля.
        
        Args:
            password (str): Пароль для проверки
            
        Returns:
            bool: True если пароль верный, иначе False
        """
        return check_password_hash(self.password, password)
    
    @property
    def full_name(self):
        """
        Возвращает полное имя пользователя.
        
        Returns:
            str: Полное имя или логин, если имя не указано
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        """
        Строковое представление объекта.
        """
        return f"<User {self.username}>" 