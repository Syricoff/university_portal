"""
Модель учебной группы.
"""
from app import db


class Group(db.Model):
    """
    Модель учебной группы студентов.
    
    Attributes:
        id (int): Уникальный идентификатор группы
        name (str): Название группы
        study_year (int): Курс обучения
        specialty (str): Специальность
    """
    __tablename__ = "groups"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    study_year = db.Column(db.Integer, nullable=False)
    specialty = db.Column(db.String(100))
    
    # Связи с другими таблицами
    students = db.relationship("Student", backref="group", cascade="all, delete-orphan")
    lessons = db.relationship("Lesson", backref="group", cascade="all, delete-orphan")
    
    def __init__(self, name, study_year, specialty=None):
        """
        Инициализация учебной группы.
        
        Args:
            name (str): Название группы
            study_year (int): Курс обучения
            specialty (str, optional): Специальность
        """
        self.name = name
        self.study_year = study_year
        self.specialty = specialty
    
    def __repr__(self):
        """
        Строковое представление объекта.
        """
        return f"<Group {self.name}>" 