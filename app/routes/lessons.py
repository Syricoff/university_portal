"""
Маршруты для управления занятиями.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.lesson import Lesson
from app.models.group import Group
from app.models.subject import Subject
from app.models.student import Student
from app.utils.decorators import login_required, admin_required
from app.models.attendance import Attendance

# Создаем Blueprint
bp = Blueprint('lessons', __name__)

@bp.route('/')
@login_required
def list():
    """
    Список занятий с фильтрацией по типу недели и группе.
    
    Returns:
        str: Отрендеренный шаблон списка занятий
    """
    week_type = request.args.get("week_type", "Обе")
    
    # Фильтрация по группе в зависимости от роли пользователя
    if session.get('user_role') == 'admin':
        group_id = request.args.get("group_id")
        groups = Group.query.all()
    elif session.get('user_role') == 'student':
        # Для студента показываем только его группу
        group_id = session.get('group_id')
        groups = [Group.query.get(group_id)]
    else:
        group_id = None
        groups = []
    
    # Базовый запрос
    query = Lesson.query
    
    # Фильтрация по типу недели
    if week_type != "Все":
        query = query.filter(db.or_(
            Lesson.week_type == week_type,
            Lesson.week_type == "Обе"
        ))
    
    # Фильтрация по группе, если выбрана
    if group_id:
        query = query.filter_by(group_id=group_id)
    
    # Получение и группировка занятий по дням недели
    lessons = query.order_by(Lesson.day_of_week, Lesson.lesson_number).all()
    
    # Группировка занятий по дням недели
    days_order = {"Пн": 1, "Вт": 2, "Ср": 3, "Чт": 4, "Пт": 5, "Сб": 6}
    lessons_by_day = {}
    
    for day_code in days_order.keys():
        lessons_by_day[day_code] = []
    
    for lesson in lessons:
        if lesson.day_of_week in lessons_by_day:
            lessons_by_day[lesson.day_of_week].append(lesson)
    
    # Определяем, имеет ли пользователь право на редактирование
    can_edit = session.get('user_role') == 'admin'
    
    return render_template(
        "lessons/list.html", 
        lessons_by_day=lessons_by_day, 
        days_order=days_order,
        week_type=week_type,
        selected_group_id=group_id,
        groups=groups,
        can_edit=can_edit
    )


@bp.route('/create', methods=["GET", "POST"])
@admin_required
def create():
    """
    Создание нового занятия.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    if request.method == "POST":
        lesson = Lesson(
            subject_id=int(request.form["subject_id"]),
            group_id=int(request.form["group_id"]),
            lesson_type=request.form["lesson_type"],
            week_type=request.form["week_type"],
            day_of_week=request.form["day_of_week"],
            lesson_number=int(request.form["lesson_number"])
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Занятие создано", "success")
        return redirect(url_for('lessons.list'))
    
    subjects = Subject.query.all()
    groups = Group.query.all()
    
    # Передаем константы для выпадающих списков
    week_types = Lesson.WEEK_TYPES
    lesson_types = Lesson.LESSON_TYPES
    days_of_week = Lesson.DAYS_OF_WEEK
    
    return render_template(
        "lessons/create.html", 
        subjects=subjects, 
        groups=groups,
        week_types=week_types,
        lesson_types=lesson_types,
        days_of_week=days_of_week
    )


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@admin_required
def edit(id):
    """
    Редактирование существующего занятия.
    
    Args:
        id (int): Идентификатор занятия
        
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    lesson = Lesson.query.get_or_404(id)
    if request.method == "POST":
        lesson.subject_id = int(request.form["subject_id"])
        lesson.group_id = int(request.form["group_id"])
        lesson.lesson_type = request.form["lesson_type"]
        lesson.week_type = request.form["week_type"]
        lesson.day_of_week = request.form["day_of_week"]
        lesson.lesson_number = int(request.form["lesson_number"])
        db.session.commit()
        flash("Данные занятия обновлены", "success")
        return redirect(url_for('lessons.list'))
    
    subjects = Subject.query.all()
    groups = Group.query.all()
    
    # Передаем константы для выпадающих списков
    week_types = Lesson.WEEK_TYPES
    lesson_types = Lesson.LESSON_TYPES
    days_of_week = Lesson.DAYS_OF_WEEK
    
    return render_template(
        "lessons/edit.html", 
        lesson=lesson, 
        subjects=subjects, 
        groups=groups,
        week_types=week_types,
        lesson_types=lesson_types,
        days_of_week=days_of_week
    )


@bp.route('/delete/<int:id>', methods=["POST"])
@admin_required
def delete(id):
    """
    Удаление занятия.
    
    Args:
        id (int): Идентификатор занятия
        
    Returns:
        Response: Перенаправление на список занятий
    """
    lesson = Lesson.query.get_or_404(id)
    
    # Сначала удаляем все записи посещаемости для этого занятия
    Attendance.query.filter_by(lesson_id=lesson.id).delete()
    
    # Затем удаляем само занятие
    db.session.delete(lesson)
    db.session.commit()
    flash("Занятие удалено", "warning")
    return redirect(url_for('lessons.list')) 