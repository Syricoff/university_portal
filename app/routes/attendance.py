"""
Маршруты для управления посещаемостью.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from datetime import datetime, timedelta
from app import db
from app.models.attendance import Attendance
from app.models.lesson import Lesson
from app.models.student import Student
from app.models.group import Group
from app.models.subject import Subject
from app.utils.decorators import login_required, admin_required, admin_or_group_admin_required

# Создаем Blueprint
bp = Blueprint('attendance', __name__)

@bp.route('/')
@login_required
def list():
    """
    Список посещаемости с фильтрацией по дате, группе, студенту и предмету.
    
    Returns:
        str: Отрендеренный шаблон списка посещаемости
    """
    # Получаем параметры фильтрации
    start_date = request.args.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    end_date = request.args.get("end_date", datetime.now().strftime("%Y-%m-%d"))
    group_id = request.args.get("group_id")
    student_id = request.args.get("student_id")
    subject_id = request.args.get("subject_id")
    
    # Преобразуем даты из строк в объекты date
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Базовый запрос
    query = Attendance.query.filter(
        Attendance.date >= start_date_obj,
        Attendance.date <= end_date_obj
    )
    
    # Фильтрация в зависимости от роли пользователя
    user_role = session.get('user_role')
    
    # Для обычного студента показываем только его посещаемость
    if user_role == 'student' and not session.get('is_group_admin', False):
        student_id = session.get('student_id')
        query = query.filter_by(student_id=student_id)
        
    # Для старосты группы показываем посещаемость его группы
    elif user_role == 'student' and session.get('is_group_admin', False):
        if not group_id:  # Если группа не задана явно в фильтрах, используем группу старосты
            group_id = session.get('group_id')
            
        student_ids = [s.id for s in Student.query.filter_by(group_id=group_id).all()]
        query = query.filter(Attendance.student_id.in_(student_ids))
        
    # Для администратора доступны все записи, применяем фильтры если они указаны
    else:  # admin
        # Фильтрация по группе, если выбрана
        if group_id:
            if not student_id:
                # Только по группе - получаем всех студентов группы
                student_ids = [student.id for student in Student.query.filter_by(group_id=group_id).all()]
                query = query.filter(Attendance.student_id.in_(student_ids))
        
    # Фильтрация по студенту, если выбран и пользователь имеет право
    if student_id and (user_role == 'admin' or 
                     (user_role == 'student' and session.get('is_group_admin') and 
                      Student.query.get(student_id).group_id == session.get('group_id'))):
        query = query.filter_by(student_id=student_id)
    
    # Фильтрация по предмету, если выбран
    if subject_id:
        # Получаем все занятия по данному предмету
        lesson_ids = [lesson.id for lesson in Lesson.query.filter_by(subject_id=subject_id).all()]
        if lesson_ids:
            query = query.filter(Attendance.lesson_id.in_(lesson_ids))
    
    # Выполняем запрос
    attendance_records = query.order_by(Attendance.date.desc(), Attendance.lesson_id).all()
    
    # Получаем списки для фильтров в зависимости от роли
    if user_role == 'admin':
        groups = Group.query.all()
        # Если выбрана группа, отображаем только студентов этой группы
        if group_id:
            students = Student.query.filter_by(group_id=group_id).all()
        else:
            students = Student.query.all()
    elif user_role == 'student' and session.get('is_group_admin'):
        # Староста видит только свою группу
        groups = [Group.query.get(session.get('group_id'))]
        students = Student.query.filter_by(group_id=session.get('group_id')).all()
    else:
        # Обычный студент видит только себя
        groups = [Group.query.get(session.get('group_id'))]
        students = [Student.query.get(session.get('student_id'))]
    
    subjects = Subject.query.all()
    
    # Определяем, имеет ли пользователь право на редактирование
    can_edit = user_role == 'admin' or (user_role == 'student' and session.get('is_group_admin'))
    
    return render_template(
        "attendance/list.html", 
        attendance=attendance_records,
        start_date=start_date,
        end_date=end_date,
        selected_group_id=group_id,
        selected_student_id=student_id,
        selected_subject_id=subject_id,
        groups=groups,
        students=students,
        subjects=subjects,
        can_edit=can_edit
    )


@bp.route('/create', methods=["GET", "POST"])
@admin_or_group_admin_required
def create(group_admin_group_id=None):
    """
    Создание новой записи о посещаемости.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    if request.method == "POST":
        lesson_id = int(request.form["lesson_id"])
        student_id = int(request.form["student_id"])
        
        # Проверка доступа для старост групп
        if session.get('user_role') == 'student' and session.get('is_group_admin'):
            # Используем group_admin_group_id вместо session.get('group_id')
            # Проверяем, что выбранный студент из группы старосты
            student = Student.query.get(student_id)
            if student.group_id != group_admin_group_id:
                flash("Вы можете добавлять посещаемость только для студентов вашей группы", "danger")
                return redirect(url_for('attendance.list'))
                
            # Проверяем, что выбранное занятие относится к группе старосты
            lesson = Lesson.query.get(lesson_id)
            if lesson.group_id != group_admin_group_id:
                flash("Вы можете добавлять посещаемость только для занятий вашей группы", "danger")
                return redirect(url_for('attendance.list'))
                
        attendance = Attendance(
            lesson_id=lesson_id,
            student_id=student_id,
            date=datetime.strptime(request.form["date"], "%Y-%m-%d"),
            status=request.form["status"]
        )
        db.session.add(attendance)
        db.session.commit()
        flash("Посещаемость добавлена", "success")
        return redirect(url_for('attendance.list'))
    
    # Фильтруем данные по роли пользователя
    if session.get('user_role') == 'admin':
        lessons = Lesson.query.all()
        students = Student.query.all()
        groups = Group.query.all()
    else:  # староста группы
        # Используем group_admin_group_id вместо session.get('group_id')
        lessons = Lesson.query.filter_by(group_id=group_admin_group_id).all()
        students = Student.query.filter_by(group_id=group_admin_group_id).all()
        groups = [Group.query.get(group_admin_group_id)]
        
    statuses = Attendance.STATUSES
    status_labels = Attendance.STATUS_LABELS
    
    return render_template(
        "attendance/create.html", 
        lessons=lessons, 
        students=students, 
        groups=groups,
        statuses=statuses,
        status_labels=status_labels
    )


@bp.route('/bulk', methods=["GET", "POST"])
@admin_or_group_admin_required
def bulk(group_admin_group_id=None):
    """
    Массовое заполнение посещаемости для группы.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на страницу
    """
    if request.method == "POST":
        # Получение данных из формы
        date_str = request.form["date"]
        date = datetime.strptime(date_str, "%Y-%m-%d").date()  # Берем только дату без времени
        lesson_id = int(request.form["lesson_id"])
        
        # Проверка доступа для старост групп
        if session.get('user_role') == 'student' and session.get('is_group_admin'):
            # Используем group_admin_group_id вместо session.get('group_id')
            # Проверяем, что выбранное занятие относится к группе старосты
            lesson = Lesson.query.get(lesson_id)
            if lesson.group_id != group_admin_group_id:
                flash("Вы можете добавлять посещаемость только для занятий вашей группы", "danger")
                return redirect(url_for('attendance.bulk'))
        
        student_statuses = {}
        
        # Получаем все ID студентов и их статусы
        for key, value in request.form.items():
            if key.startswith("student_"):
                student_id = int(key.split("_")[1])
                
                # Дополнительная проверка для старост
                if session.get('user_role') == 'student' and session.get('is_group_admin'):
                    student = Student.query.get(student_id)
                    # Используем group_admin_group_id вместо session.get('group_id')
                    if student.group_id != group_admin_group_id:
                        continue  # Пропускаем студентов не из своей группы
                        
                student_statuses[student_id] = value
        
        # Проверяем существующие записи и обновляем или добавляем
        for student_id, status in student_statuses.items():
            # Проверка, что student_id существует и не None
            if student_id is None:
                continue
                
            # Находим все существующие записи для этого студента, урока и даты (могут быть дубликаты)
            existing_records = Attendance.query.filter_by(
                student_id=student_id,
                lesson_id=lesson_id,
                date=date
            ).all()
            
            if existing_records:
                # Если есть дубликаты, удаляем все кроме первой записи
                if len(existing_records) > 1:
                    print(f"Найдено {len(existing_records)} дубликатов для студента {student_id} на {date}")
                    # Оставляем только первую запись
                    for record in existing_records[1:]:
                        print(f"Удаляем дубликат: ID={record.id}")
                        db.session.delete(record)
                
                # Обновляем первую запись
                existing_records[0].status = status
                print(f"Обновляем запись: ID={existing_records[0].id}, студент={student_id}, статус={status}")
            else:
                # Создаем новую запись
                attendance = Attendance(
                    lesson_id=lesson_id,
                    student_id=student_id,
                    date=date,
                    status=status
                )
                print(f"Создаем новую запись: студент={student_id}, статус={status}")
                db.session.add(attendance)
        
        db.session.commit()
        flash("Посещаемость успешно сохранена", "success")
        return redirect(url_for('attendance.bulk'))
    
    # Для GET-запроса подготавливаем форму
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    # Фильтруем данные в зависимости от роли пользователя
    if session.get('user_role') == 'admin':
        group_id = request.args.get("group_id")
        groups = Group.query.all()
    else:  # староста группы
        # Используем group_admin_group_id вместо session.get('group_id')
        group_id = group_admin_group_id
        groups = [Group.query.get(group_id)]
    
    lesson_id = request.args.get("lesson_id")
    
    # Если выбрана группа, получаем список занятий для этой группы
    lessons = []
    if group_id:
        lessons = Lesson.query.filter_by(group_id=group_id).all()
    
    # Получаем список студентов для выбранной группы
    students = []
    if group_id:
        students = Student.query.filter_by(group_id=group_id).all()
    
    # Получаем существующие записи о посещаемости, если выбраны все параметры
    attendance_records = {}
    if date and lesson_id and group_id:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()  # Берем только дату без времени
        
        # Получаем список студентов в группе
        students_in_group = Student.query.filter_by(group_id=group_id).all()
        student_ids = [student.id for student in students_in_group]
        
        # Получаем все записи посещаемости для всех студентов группы на указанную дату и занятие
        all_records = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.lesson_id == lesson_id,
            Attendance.date == date_obj
        ).all()
        
        # Группируем записи по ID студента для обработки дубликатов
        records_by_student = {}
        for record in all_records:
            if record.student_id not in records_by_student:
                records_by_student[record.student_id] = []
            records_by_student[record.student_id].append(record)
        
        # Для каждого студента берем последнюю запись (предполагая, что это самая актуальная)
        for student_id, records in records_by_student.items():
            if len(records) > 1:
                print(f"Внимание: найдено {len(records)} записей для студента {student_id} на дату {date_obj} и урок {lesson_id}")
                # Сортируем по ID (предполагая, что больший ID = более поздняя запись)
                records.sort(key=lambda r: r.id, reverse=True)
            
            # Используем первую запись из отсортированного списка (самую последнюю)
            latest_record = records[0]
            attendance_records[student_id] = latest_record.status
            print(f"Выбрана запись: ID={latest_record.id}, студент={student_id}, статус={latest_record.status}")
    
    statuses = Attendance.STATUSES
    status_labels = Attendance.STATUS_LABELS
    
    return render_template(
        "attendance/bulk.html",
        date=date,
        selected_group_id=group_id,
        selected_lesson_id=lesson_id,
        groups=groups,
        lessons=lessons,
        students=students,
        attendance_records=attendance_records,
        statuses=statuses,
        status_labels=status_labels
    )


@bp.route('/report')
@login_required
def report():
    """
    Отчет по посещаемости с агрегированными данными.
    
    Returns:
        str: Отрендеренный шаблон отчета
    """
    # Получаем параметры фильтрации
    start_date = request.args.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    end_date = request.args.get("end_date", datetime.now().strftime("%Y-%m-%d"))
    subject_id = request.args.get("subject_id")
    
    # Преобразуем даты из строк в объекты date
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Фильтруем данные в зависимости от роли пользователя
    if session.get('user_role') == 'admin':
        group_id = request.args.get("group_id")
        groups = Group.query.all()
    elif session.get('user_role') == 'student' and session.get('is_group_admin'):
        # Староста группы видит только свою группу
        group_id = session.get('group_id')
        groups = [Group.query.get(group_id)]
    else:  # обычный студент
        group_id = session.get('group_id')
        groups = [Group.query.get(group_id)]
        
    # Подготавливаем запрос в зависимости от наличия фильтра по группе и предмету
    query = """
        SELECT s.id as student_id, u.first_name, u.last_name, g.name as group_name,
               COUNT(a.id) as total, 
               SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as presents
        FROM students s
        JOIN users u ON s.user_id = u.id
        JOIN groups g ON s.group_id = g.id
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date BETWEEN :start_date AND :end_date
    """
    
    params = {"start_date": start_date_obj, "end_date": end_date_obj}
    
    # Добавляем условия для фильтрации по предмету
    if subject_id:
        query = """
            SELECT s.id as student_id, u.first_name, u.last_name, g.name as group_name,
                   COUNT(a.id) as total, 
                   SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as presents
            FROM students s
            JOIN users u ON s.user_id = u.id
            JOIN groups g ON s.group_id = g.id
            LEFT JOIN attendance a ON s.id = a.student_id AND a.date BETWEEN :start_date AND :end_date
            LEFT JOIN lessons l ON a.lesson_id = l.id
            WHERE l.subject_id = :subject_id
        """
        params["subject_id"] = subject_id
    
    # Добавляем условия для группы
    if group_id:
        if "WHERE" in query:
            query += " AND s.group_id = :group_id"
        else:
            query += " WHERE s.group_id = :group_id"
        params["group_id"] = group_id
    
    # Для обычного студента показываем только его данные
    if session.get('user_role') == 'student' and not session.get('is_group_admin'):
        if "WHERE" in query:
            query += " AND s.id = :student_id"
        else:
            query += " WHERE s.id = :student_id"
        params["student_id"] = session.get('student_id')
        
    query += " GROUP BY s.id, u.first_name, u.last_name, g.name"
    
    report_data = db.session.execute(text(query), params)
    
    subjects = Subject.query.all()
    
    return render_template(
        "attendance/report.html", 
        report=report_data,
        start_date=start_date,
        end_date=end_date,
        selected_group_id=group_id,
        selected_subject_id=subject_id,
        groups=groups,
        subjects=subjects
    ) 