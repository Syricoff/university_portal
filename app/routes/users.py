"""
Маршруты для управления пользователями.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance
from app.utils.decorators import admin_required

# Создаем Blueprint
bp = Blueprint('users', __name__)

@bp.route('/')
@admin_required
def list():
    """
    Список пользователей с возможностью поиска.
    
    Returns:
        str: Отрендеренный шаблон списка пользователей
    """
    search = request.args.get("search", "")
    if search:
        users = User.query.filter(
            db.or_(
                User.username.contains(search),
                User.first_name.contains(search),
                User.last_name.contains(search)
            )
        ).all()
    else:
        users = User.query.all()
    return render_template("users/list.html", users=users)


@bp.route('/create', methods=["GET", "POST"])
@admin_required
def create():
    """
    Создание нового пользователя.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=request.form["password"],
            role=request.form["role"],
            first_name=request.form.get("first_name"),
            last_name=request.form.get("last_name"),
        )
        db.session.add(user)
        db.session.commit()
        flash("Пользователь создан", "success")
        return redirect(url_for('users.list'))
    return render_template("users/create.html")


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@admin_required
def edit(id):
    """
    Редактирование существующего пользователя.
    
    Args:
        id (int): Идентификатор пользователя
        
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление на список
    """
    user = User.query.get_or_404(id)
    if request.method == "POST":
        user.username = request.form["username"]
        user.role = request.form["role"]
        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        
        # Обновляем пароль только если он был введен
        if request.form.get("password"):
            user.password = generate_password_hash(request.form["password"])
            
        db.session.commit()
        flash("Данные пользователя обновлены", "success")
        return redirect(url_for('users.list'))
    return render_template("users/edit.html", user=user)


@bp.route('/delete/<int:id>', methods=["POST"])
@admin_required
def delete(id):
    """
    Удаление пользователя.
    
    Args:
        id (int): Идентификатор пользователя
        
    Returns:
        Response: Перенаправление на список пользователей
    """
    user = User.query.get_or_404(id)
    
    # Проверяем, является ли пользователь студентом
    student = Student.query.filter_by(user_id=user.id).first()
    if student:
        # Удаляем записи посещаемости для этого студента
        Attendance.query.filter_by(student_id=student.id).delete()
        
        # Удаляем запись студента
        db.session.delete(student)
    
    # Затем удаляем самого пользователя
    db.session.delete(user)
    db.session.commit()
    flash("Пользователь удален", "warning")
    return redirect(url_for('users.list')) 