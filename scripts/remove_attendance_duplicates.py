#!/usr/bin/env python
"""
Скрипт для удаления дубликатов записей посещаемости.
Запуск: python scripts/remove_attendance_duplicates.py
"""
import sys
import os
from sqlalchemy import func

# Добавляем корневую папку проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.attendance import Attendance


def remove_duplicates():
    """
    Удаляет дублирующиеся записи посещаемости.
    Дубликатами считаются записи с одинаковыми student_id, lesson_id и date.
    """
    print("Поиск дубликатов записей посещаемости...")
    
    # Находим комбинации student_id, lesson_id, date с более чем 1 записью
    duplicates = db.session.query(
        Attendance.student_id, 
        Attendance.lesson_id, 
        Attendance.date,
        func.count('*').label('count')
    ).group_by(
        Attendance.student_id, 
        Attendance.lesson_id, 
        Attendance.date
    ).having(
        func.count('*') > 1
    ).all()
    
    print(f"Найдено {len(duplicates)} комбинаций с дубликатами")
    
    total_deleted = 0
    
    # Для каждой комбинации с дубликатами
    for student_id, lesson_id, date, count in duplicates:
        # Находим все записи для этой комбинации
        duplicate_records = Attendance.query.filter_by(
            student_id=student_id,
            lesson_id=lesson_id,
            date=date
        ).order_by(Attendance.id).all()
        
        print(f"Дубликаты для студента {student_id}, занятия {lesson_id}, даты {date}:")
        print(f"  Всего записей: {count}")
        
        # Оставляем только первую запись (с наименьшим id)
        first_record = duplicate_records[0]
        print(f"  Оставляем запись с id={first_record.id}, статус={first_record.status}")
        
        # Удаляем все остальные записи
        for record in duplicate_records[1:]:
            print(f"  Удаляем запись с id={record.id}, статус={record.status}")
            db.session.delete(record)
            total_deleted += 1
    
    # Сохраняем изменения
    db.session.commit()
    
    print(f"Всего удалено {total_deleted} дублирующихся записей")
    print("Операция завершена успешно!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        remove_duplicates() 