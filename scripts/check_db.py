"""
Скрипт для проверки состояния базы данных и вывода статистики.
"""
from app import create_app, db
from app.models.user import User
from app.models.group import Group
from app.models.student import Student
from app.models.subject import Subject
from app.models.lesson import Lesson
from app.models.attendance import Attendance

app = create_app()

def check_database():
    """
    Выводит статистику по таблицам базы данных.
    """
    with app.app_context():
        print("=== Статистика базы данных ===")
        
        # Пользователи
        users = User.query.all()
        users_by_role = {}
        for user in users:
            if user.role not in users_by_role:
                users_by_role[user.role] = 0
            users_by_role[user.role] += 1
        
        print(f"Пользователей: {len(users)}")
        for role, count in users_by_role.items():
            print(f"  - {role}: {count}")
        
        # Группы
        groups = Group.query.all()
        print(f"Групп: {len(groups)}")
        for group in groups:
            student_count = Student.query.filter_by(group_id=group.id).count()
            print(f"  - {group.name} ({group.specialty}): {student_count} студентов")
        
        # Студенты
        students = Student.query.all()
        print(f"Студентов: {len(students)}")
        admin_count = Student.query.filter_by(is_group_admin=True).count()
        print(f"  - Старост: {admin_count}")
        
        # Предметы
        subjects = Subject.query.all()
        print(f"Предметов: {len(subjects)}")
        
        # Занятия
        lessons = Lesson.query.all()
        lessons_by_type = {}
        for lesson in lessons:
            if lesson.lesson_type not in lessons_by_type:
                lessons_by_type[lesson.lesson_type] = 0
            lessons_by_type[lesson.lesson_type] += 1
        
        print(f"Занятий: {len(lessons)}")
        for lesson_type, count in lessons_by_type.items():
            print(f"  - {lesson_type}: {count}")
        
        # Посещаемость
        attendance = Attendance.query.all()
        attendance_by_status = {}
        for record in attendance:
            if record.status not in attendance_by_status:
                attendance_by_status[record.status] = 0
            attendance_by_status[record.status] += 1
        
        print(f"Записей посещаемости: {len(attendance)}")
        for status, count in attendance_by_status.items():
            status_label = Attendance.STATUS_LABELS.get(status, status)
            print(f"  - {status_label}: {count}")

if __name__ == "__main__":
    check_database() 