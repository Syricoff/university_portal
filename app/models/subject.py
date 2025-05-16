"""
Модель учебного предмета.
"""
from app import db


class Subject(db.Model):
    """
    Модель учебного предмета.
    
    Attributes:
        id (int): Уникальный идентификатор предмета
        name (str): Название предмета
    """
    __tablename__ = "subjects"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    
    # Связи с другими таблицами
    lessons = db.relationship("Lesson", backref="subject", cascade="all, delete-orphan")
    
    def __init__(self, name):
        """
        Инициализация предмета.
        
        Args:
            name (str): Название предмета
        """
        self.name = name
    
    def __repr__(self):
        """
        Строковое представление объекта.
        """
        return f"<Subject {self.name}>" 