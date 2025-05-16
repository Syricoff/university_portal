"""
Скрипт для заполнения базы данных тестовыми данными.
Запуск: python scripts/seed_data.py
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Добавляем корневую папку проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.group import Group
from app.models.student import Student
from app.models.subject import Subject
from app.models.lesson import Lesson
from app.models.attendance import Attendance


def clear_tables():
    """Очищает все таблицы базы данных."""
    print("Очистка таблиц...")
    
    # Очищаем таблицы в правильном порядке, чтобы избежать проблем с внешними ключами
    Attendance.query.delete()
    Student.query.delete()
    Lesson.query.delete()
    Subject.query.delete()
    Group.query.delete()
    User.query.delete()
    
    db.session.commit()
    print("Таблицы очищены.")


def seed_data():
    """Заполняет базу данных тестовыми данными."""
    
    # Пользователи
    print("Создание пользователей...")
    admin = User(
        username="admin",
        password="admin123",
        role="admin",
        first_name="Администратор",
        last_name="Системы"
    )
    
    # Создание обычных пользователей
    users = [
        User(username="user1", password="password", role="student", first_name="Иван", last_name="Иванов"),
        User(username="user2", password="password", role="student", first_name="Петр", last_name="Петров"),
        User(username="user3", password="password", role="student", first_name="Алексей", last_name="Сидоров"),
        User(username="user4", password="password", role="student", first_name="Ольга", last_name="Смирнова"),
        User(username="user5", password="password", role="student", first_name="Анна", last_name="Кузнецова"),
        User(username="user6", password="password", role="student", first_name="Мария", last_name="Попова"),
        User(username="user7", password="password", role="student", first_name="Сергей", last_name="Васильев"),
        User(username="user8", password="password", role="student", first_name="Дмитрий", last_name="Соколов")
    ]
    
    db.session.add(admin)
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    print(f"Создано {len(users) + 1} пользователей")
    
    # Группы
    print("Создание групп...")
    groups = [
        Group(name="ИС-11", study_year=1, specialty="Информационные системы"),
        Group(name="ИБ-21", study_year=2, specialty="Информационная безопасность")
    ]
    
    for group in groups:
        db.session.add(group)
    
    db.session.commit()
    print(f"Создано {len(groups)} групп")
    
    # Студенты
    print("Создание студентов...")
    students = [
        Student(user_id=users[0].id, group_id=groups[0].id, is_group_admin=True),  # староста первой группы
        Student(user_id=users[1].id, group_id=groups[0].id),
        Student(user_id=users[2].id, group_id=groups[0].id),
        Student(user_id=users[3].id, group_id=groups[0].id),
        Student(user_id=users[4].id, group_id=groups[1].id, is_group_admin=True),  # староста второй группы
        Student(user_id=users[5].id, group_id=groups[1].id),
        Student(user_id=users[6].id, group_id=groups[1].id),
        Student(user_id=users[7].id, group_id=groups[1].id)
    ]
    
    for student in students:
        db.session.add(student)
    
    db.session.commit()
    print(f"Создано {len(students)} студентов")
    
    # Предметы
    print("Создание предметов...")
    subjects = [
        Subject(name="Математический анализ"),
        Subject(name="Программирование"),
        Subject(name="Базы данных"),
        Subject(name="Операционные системы"),
        Subject(name="Сети и телекоммуникации")
    ]
    
    for subject in subjects:
        db.session.add(subject)
    
    db.session.commit()
    print(f"Создано {len(subjects)} предметов")
    
    # Занятия
    print("Создание занятий...")
    lessons = []
    
    # Занятия для первой группы
    lessons.extend([
        Lesson(subject_id=subjects[0].id, group_id=groups[0].id, lesson_type="Лекция", week_type="Обе", day_of_week="Пн", lesson_number=1),
        Lesson(subject_id=subjects[1].id, group_id=groups[0].id, lesson_type="Практика", week_type="Обе", day_of_week="Пн", lesson_number=2),
        Lesson(subject_id=subjects[2].id, group_id=groups[0].id, lesson_type="Лаб", week_type="Чет", day_of_week="Вт", lesson_number=1),
        Lesson(subject_id=subjects[3].id, group_id=groups[0].id, lesson_type="Семинар", week_type="Нечет", day_of_week="Ср", lesson_number=3)
    ])
    
    # Занятия для второй группы
    lessons.extend([
        Lesson(subject_id=subjects[0].id, group_id=groups[1].id, lesson_type="Лекция", week_type="Обе", day_of_week="Чт", lesson_number=1),
        Lesson(subject_id=subjects[4].id, group_id=groups[1].id, lesson_type="Лаб", week_type="Обе", day_of_week="Пт", lesson_number=2),
        Lesson(subject_id=subjects[3].id, group_id=groups[1].id, lesson_type="Практика", week_type="Чет", day_of_week="Сб", lesson_number=1)
    ])
    
    for lesson in lessons:
        db.session.add(lesson)
    
    db.session.commit()
    print(f"Создано {len(lessons)} занятий")
    
    # Посещаемость
    print("Создание записей о посещаемости...")
    attendances = []
    
    # Генерируем посещаемость за последний месяц
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    # Статусы посещения
    statuses = ["present", "absent", "late", "sick"]
    # Вероятности для каждого статуса (present: 70%, absent: 10%, late: 10%, sick: 10%)
    status_weights = [0.7, 0.1, 0.1, 0.1]
    
    # Для каждого занятия
    for lesson in lessons:
        # Для каждого студента в группе урока
        for student in Student.query.filter_by(group_id=lesson.group_id).all():
            # Генерируем несколько дат посещения
            for i in range(4):
                # Случайная дата в пределах месяца
                random_days = random.randint(0, 30)
                date = start_date + timedelta(days=random_days)
                
                # Случайный статус с учетом весов
                status = random.choices(statuses, weights=status_weights)[0]
                
                # Проверяем, не существует ли уже такая запись
                existing = Attendance.query.filter_by(
                    lesson_id=lesson.id,
                    student_id=student.id,
                    date=date
                ).first()
                
                if not existing:
                    attendance = Attendance(
                        lesson_id=lesson.id,
                        student_id=student.id,
                        date=date,
                        status=status
                    )
                    attendances.append(attendance)
    
    for attendance in attendances:
        db.session.add(attendance)
    
    db.session.commit()
    print(f"Создано {len(attendances)} записей о посещаемости")
    print("База данных успешно заполнена тестовыми данными!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Очищаем таблицы перед заполнением, если это необходимо
        answer = input("Очистить существующие данные перед заполнением? (y/n): ")
        if answer.lower() == "y":
            clear_tables()
        
        # Заполняем таблицы тестовыми данными
        seed_data() 