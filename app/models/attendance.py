"""
Модель посещаемости занятий.
"""
from app import db
from datetime import datetime


class Attendance(db.Model):
    """
    Модель посещаемости занятий студентами.
    
    Attributes:
        id (int): Уникальный идентификатор записи
        lesson_id (int): Идентификатор занятия
        student_id (int): Идентификатор студента
        date (datetime.date): Дата занятия
        status (str): Статус посещения (present, absent, late, sick)
    """
    __tablename__ = "attendance"
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10))
    
    # Добавляем уникальное ограничение для предотвращения дубликатов
    __table_args__ = (
        db.UniqueConstraint('student_id', 'lesson_id', 'date', name='uix_attendance_student_lesson_date'),
    )
    
    # Связи с другими таблицами через backref
    # student и lesson присваиваются через backref в их моделях
    
    # Константы для статусов посещения
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_SICK = 'sick'
    
    STATUSES = [STATUS_PRESENT, STATUS_ABSENT, STATUS_LATE, STATUS_SICK]
    
    STATUS_LABELS = {
        STATUS_PRESENT: 'Присутствовал',
        STATUS_ABSENT: 'Отсутствовал',
        STATUS_LATE: 'Опоздал',
        STATUS_SICK: 'Болеет'
    }
    
    STATUS_COLORS = {
        STATUS_PRESENT: 'bg-success',
        STATUS_ABSENT: 'bg-danger',
        STATUS_LATE: 'bg-warning',
        STATUS_SICK: 'bg-info'
    }
    
    def __init__(self, lesson_id, student_id, date, status):
        """
        Инициализация записи о посещении.
        
        Args:
            lesson_id (int): Идентификатор занятия
            student_id (int): Идентификатор студента
            date (datetime.date): Дата занятия
            status (str): Статус посещения
        """
        self.lesson_id = lesson_id
        self.student_id = student_id
        self.date = date
        self.status = status
    
    @property
    def get_status_label(self):
        """
        Возвращает текстовую метку статуса.
        
        Returns:
            str: Текстовая метка статуса
        """
        return self.STATUS_LABELS.get(self.status, self.status)
    
    @property
    def get_status_color(self):
        """
        Возвращает класс CSS для статуса.
        
        Returns:
            str: Класс CSS
        """
        return self.STATUS_COLORS.get(self.status, 'bg-secondary')
    
    def __repr__(self):
        """
        Строковое представление объекта.
        """
        return f"<Attendance {self.student.user.username} at {self.date}>" 