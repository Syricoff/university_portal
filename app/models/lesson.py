"""
Модель учебного занятия.
"""
from app import db


class Lesson(db.Model):
    """
    Модель учебного занятия.
    
    Attributes:
        id (int): Уникальный идентификатор занятия
        subject_id (int): Идентификатор предмета
        group_id (int): Идентификатор группы
        lesson_type (str): Тип занятия (лекция, практика и т.д.)
        week_type (str): Тип недели (чет, нечет, обе)
        day_of_week (str): День недели
        lesson_number (int): Номер пары
    """
    __tablename__ = "lessons"
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    lesson_type = db.Column(db.String(10))
    week_type = db.Column(db.String(5))
    day_of_week = db.Column(db.String(10))
    lesson_number = db.Column(db.Integer, nullable=False)
    
    # Связи с другими таблицами через backref
    # subject и group присваиваются через backref в их моделях
    attendances = db.relationship("Attendance", backref="lesson", cascade="all, delete-orphan")
    
    # Константы для типов занятий и недель
    LESSON_TYPES = ['Лекция', 'Практика', 'Семинар', 'Лаб']
    WEEK_TYPES = ['Чет', 'Нечет', 'Обе']
    DAYS_OF_WEEK = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
    
    def __init__(self, subject_id, group_id, lesson_type, week_type, 
                 day_of_week, lesson_number):
        """
        Инициализация занятия.
        
        Args:
            subject_id (int): Идентификатор предмета
            group_id (int): Идентификатор группы
            lesson_type (str): Тип занятия (лекция, практика и т.д.)
            week_type (str): Тип недели (чет, нечет, обе)
            day_of_week (str): День недели
            lesson_number (int): Номер пары
        """
        self.subject_id = subject_id
        self.group_id = group_id
        self.lesson_type = lesson_type
        self.week_type = week_type
        self.day_of_week = day_of_week
        self.lesson_number = lesson_number
    
    @property
    def get_css_color(self):
        """
        Возвращает класс CSS для типа занятия.
        
        Returns:
            str: Класс CSS
        """
        color_map = {
            'Лекция': 'bg-info',
            'Практика': 'bg-success',
            'Семинар': 'bg-warning',
            'Лаб': 'bg-primary',
        }
        return color_map.get(self.lesson_type, 'bg-secondary')
    
    @property
    def week_type_color(self):
        """
        Возвращает класс CSS для типа недели.
        
        Returns:
            str: Класс CSS
        """
        color_map = {
            'Обе': 'bg-primary',
            'Чет': 'bg-success',
            'Нечет': 'bg-warning',
        }
        return color_map.get(self.week_type, 'bg-secondary')
    
    def __repr__(self):
        """
        Строковое представление объекта.
        """
        return f"<Lesson {self.subject.name} for {self.group.name}>" 