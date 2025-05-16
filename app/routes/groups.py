"""
Маршруты для управления группами.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.group import Group
from app.utils.decorators import admin_required

# Создаем Blueprint
bp = Blueprint('groups', __name__)

@bp.route('/')
@admin_required
def list():
    """
    Список групп.
    
    Returns:
        str: Отрендеренный шаблон списка групп
    """
    groups = Group.query.all()
    return render_template("groups/list.html", groups=groups)


@bp.route('/create', methods=["GET", "POST"])
@admin_required
def create():
    """
    Создание новой группы.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    if request.method == "POST":
        group = Group(
            name=request.form["name"],
            study_year=int(request.form["study_year"]),
            specialty=request.form.get("specialty")
        )
        db.session.add(group)
        db.session.commit()
        flash("Группа создана", "success")
        return redirect(url_for('groups.list'))
    return render_template("groups/create.html")


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@admin_required
def edit(id):
    """
    Редактирование существующей группы.
    
    Args:
        id (int): Идентификатор группы
        
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    group = Group.query.get_or_404(id)
    if request.method == "POST":
        group.name = request.form["name"]
        group.study_year = int(request.form["study_year"])
        group.specialty = request.form.get("specialty")
        db.session.commit()
        flash("Данные группы обновлены", "success")
        return redirect(url_for('groups.list'))
    return render_template("groups/edit.html", group=group)


@bp.route('/delete/<int:id>', methods=["POST"])
@admin_required
def delete(id):
    """
    Удаление группы.
    
    Args:
        id (int): Идентификатор группы
        
    Returns:
        Response: Перенаправление на список групп
    """
    group = Group.query.get_or_404(id)
    
    # Сначала удаляем все записи посещаемости для студентов этой группы и занятий этой группы
    from app.models.student import Student
    from app.models.lesson import Lesson
    from app.models.attendance import Attendance
    
    # Получаем всех студентов группы
    students = Student.query.filter_by(group_id=group.id).all()
    student_ids = [student.id for student in students]
    
    # Получаем все занятия группы
    lessons = Lesson.query.filter_by(group_id=group.id).all()
    lesson_ids = [lesson.id for lesson in lessons]
    
    # Удаляем записи посещаемости для этих студентов и занятий
    if student_ids:
        Attendance.query.filter(Attendance.student_id.in_(student_ids)).delete(synchronize_session=False)
    
    if lesson_ids:
        Attendance.query.filter(Attendance.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
    
    # Удаляем студентов группы
    if students:
        for student in students:
            db.session.delete(student)
    
    # Удаляем занятия группы
    if lessons:
        for lesson in lessons:
            db.session.delete(lesson)
    
    # Затем удаляем саму группу
    db.session.delete(group)
    db.session.commit()
    flash("Группа удалена", "warning")
    return redirect(url_for('groups.list')) 