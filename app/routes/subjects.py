"""
Маршруты для управления предметами.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.subject import Subject
from app.models.lesson import Lesson
from app.models.attendance import Attendance
from app.utils.decorators import admin_required

# Создаем Blueprint
bp = Blueprint('subjects', __name__)

@bp.route('/')
@admin_required
def list():
    """
    Список предметов.
    
    Returns:
        str: Отрендеренный шаблон списка предметов
    """
    subjects = Subject.query.all()
    return render_template("subjects/list.html", subjects=subjects)


@bp.route('/create', methods=["GET", "POST"])
@admin_required
def create():
    """
    Создание нового предмета.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    if request.method == "POST":
        subject = Subject(name=request.form["name"])
        db.session.add(subject)
        db.session.commit()
        flash("Предмет создан", "success")
        return redirect(url_for('subjects.list'))
    return render_template("subjects/create.html")


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@admin_required
def edit(id):
    """
    Редактирование существующего предмета.
    
    Args:
        id (int): Идентификатор предмета
        
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    subject = Subject.query.get_or_404(id)
    if request.method == "POST":
        subject.name = request.form["name"]
        db.session.commit()
        flash("Данные предмета обновлены", "success")
        return redirect(url_for('subjects.list'))
    return render_template("subjects/edit.html", subject=subject)


@bp.route('/delete/<int:id>', methods=["POST"])
@admin_required
def delete(id):
    """
    Удаление предмета.
    
    Args:
        id (int): Идентификатор предмета
        
    Returns:
        Response: Перенаправление на список предметов
    """
    subject = Subject.query.get_or_404(id)
    
    # Сначала удаляем все связанные записи
    lessons = Lesson.query.filter_by(subject_id=subject.id).all()
    lesson_ids = [lesson.id for lesson in lessons]
    
    # Удаляем записи посещаемости для этих занятий
    if lesson_ids:
        Attendance.query.filter(Attendance.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
    
    # Удаляем занятия по предмету
    if lessons:
        for lesson in lessons:
            db.session.delete(lesson)
    
    # Затем удаляем сам предмет
    db.session.delete(subject)
    db.session.commit()
    flash("Предмет удален", "warning")
    return redirect(url_for('subjects.list')) 