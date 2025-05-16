"""
Маршруты для управления студентами.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.student import Student
from app.models.user import User
from app.models.group import Group
from app.utils.decorators import admin_required
from app.models.attendance import Attendance

# Создаем Blueprint
bp = Blueprint('students', __name__)

@bp.route('/')
@admin_required
def list():
    """
    Список студентов.
    
    Returns:
        str: Отрендеренный шаблон списка студентов
    """
    students = Student.query.all()
    return render_template("students/list.html", students=students)


@bp.route('/create', methods=["GET", "POST"])
@admin_required
def create():
    """
    Создание нового студента.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    if request.method == "POST":
        user_id = int(request.form["user_id"])
        group_id = int(request.form["group_id"])
        is_group_admin = request.form.get("is_group_admin") == "on"
        
        # Проверка на уже существующего студента с тем же пользователем
        existing_student = Student.query.filter_by(user_id=user_id).first()
        if existing_student:
            flash("Этот пользователь уже является студентом", "danger")
            return redirect(url_for('students.create'))
        
        student = Student(
            user_id=user_id,
            group_id=group_id,
            is_group_admin=is_group_admin
        )
        db.session.add(student)
        db.session.commit()
        flash("Студент создан", "success")
        return redirect(url_for('students.list'))
    
    # Получаем пользователей с ролью student, которые ещё не являются студентами
    users = User.query.filter_by(role="student").all()
    available_users = []
    for user in users:
        if not user.student:
            available_users.append(user)
    
    groups = Group.query.all()
    return render_template("students/create.html", users=available_users, groups=groups)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@admin_required
def edit(id):
    """
    Редактирование существующего студента.
    
    Args:
        id (int): Идентификатор студента
        
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    student = Student.query.get_or_404(id)
    if request.method == "POST":
        student.group_id = int(request.form["group_id"])
        student.is_group_admin = request.form.get("is_group_admin") == "on"
        db.session.commit()
        flash("Данные студента обновлены", "success")
        return redirect(url_for('students.list'))
    
    users = [student.user]  # В редактировании пользователя менять нельзя
    groups = Group.query.all()
    return render_template("students/edit.html", student=student, users=users, groups=groups)


@bp.route('/delete/<int:id>', methods=["POST"])
@admin_required
def delete(id):
    """
    Удаление студента.
    
    Args:
        id (int): Идентификатор студента
        
    Returns:
        Response: Перенаправление на список студентов
    """
    student = Student.query.get_or_404(id)
    
    # Сначала удаляем все записи посещаемости для этого студента
    Attendance.query.filter_by(student_id=student.id).delete()
    
    # Затем удаляем самого студента
    db.session.delete(student)
    db.session.commit()
    flash("Студент удален", "warning")
    return redirect(url_for('students.list')) 