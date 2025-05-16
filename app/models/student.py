"""
Модель студента.
"""
from app import db


class Student(db.Model):
    """
    Модель студента с привязкой к пользователю и группе.
    
    Attributes:
        id (int): Уникальный идентификатор студента
        user_id (int): Идентификатор пользователя
        group_id (int): Идентификатор группы
        is_group_admin (bool): Флаг старосты группы
    """
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    is_group_admin = db.Column(db.Boolean, default=False)
    
    # Связи с другими таблицами через backref
    # user и group присваиваются через backref в их моделях
    attendances = db.relationship("Attendance", backref="student", cascade="all, delete-orphan")
    
    def __init__(self, user_id, group_id, is_group_admin=False):
        """
        Инициализация студента.
        
        Args:
            user_id (int): Идентификатор пользователя
            group_id (int): Идентификатор группы
            is_group_admin (bool, optional): Является ли старостой группы
        """
        self.user_id = user_id
        self.group_id = group_id
        self.is_group_admin = is_group_admin
    
    @property
    def full_name(self):
        """
        Возвращает полное имя студента.
        
        Returns:
            str: Полное имя студента
        """
        return self.user.full_name
    
    @property
    def username(self):
        """
        Возвращает логин студента.
        
        Returns:
            str: Логин студента
        """
        return self.user.username
    
    def __repr__(self):
        """
        Строковое представление объекта.
        """
        return f"<Student {self.user.username}>" 