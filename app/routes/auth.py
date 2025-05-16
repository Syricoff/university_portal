"""
Маршруты для аутентификации пользователей.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.student import Student

# Создаем Blueprint
bp = Blueprint('auth', __name__)

@bp.route('/login', methods=["GET", "POST"])
def login():
    """
    Страница входа в систему.
    
    Returns:
        str или Response: Отрендеренный шаблон формы или перенаправление
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Успешная аутентификация
            session["user_id"] = user.id
            session["username"] = user.username
            session["user_role"] = user.role
            session["user_fullname"] = user.full_name
            
            # Если пользователь - студент, добавляем информацию о студенте
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    session["student_id"] = student.id
                    session["group_id"] = student.group_id
                    session["is_group_admin"] = student.is_group_admin
            
            flash(f"Добро пожаловать, {user.first_name or user.username}!", "success")
            
            # Перенаправление на запрошенную страницу или на главную
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash("Неверное имя пользователя или пароль", "danger")
    
    return render_template("auth/login.html")


@bp.route('/logout')
def logout():
    """
    Выход из системы.
    
    Returns:
        Response: Перенаправление на страницу входа
    """
    # Удаляем данные сессии
    session.clear()
    
    flash("Вы вышли из системы", "info")
    return redirect(url_for('auth.login')) 