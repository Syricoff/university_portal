"""
Декораторы для маршрутов и функций.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request
from app.models.student import Student
from app import db


def login_required(f):
    """
    Декоратор для проверки авторизации пользователя.
    
    Args:
        f (function): Декорируемая функция
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Необходимо авторизоваться для доступа к этой странице', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Декоратор для проверки прав администратора.
    
    Args:
        f (function): Декорируемая функция
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash('У вас нет прав для доступа к этой странице', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Декоратор для проверки роли студента.
    
    Args:
        f (function): Декорируемая функция
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'student':
            flash('Эта страница доступна только для студентов', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def group_admin_required(f):
    """
    Декоратор для проверки роли старосты группы.
    
    Args:
        f (function): Декорируемая функция
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'student':
            flash('У вас нет прав для доступа к этой странице', 'danger')
            return redirect(url_for('main.index'))
        
        # Проверяем, является ли студент старостой группы
        student = Student.query.filter_by(user_id=session['user_id'], is_group_admin=True).first()
        if not student:
            flash('Эта страница доступна только для старост группы', 'danger')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function


def admin_or_group_admin_required(f):
    """
    Декоратор для проверки прав администратора или старосты группы.
    
    Args:
        f (function): Декорируемая функция
        
    Returns:
        function: Обернутая функция
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session:
            flash('Необходимо авторизоваться для доступа к этой странице', 'warning')
            return redirect(url_for('auth.login', next=request.url))
            
        # Проверка на администратора
        if session['user_role'] == 'admin':
            return f(*args, **kwargs)
            
        # Проверка на старосту группы
        if session['user_role'] == 'student':
            student = Student.query.filter_by(user_id=session['user_id'], is_group_admin=True).first()
            if student:
                # Добавим ID группы в kwargs для дальнейшего использования
                kwargs['group_admin_group_id'] = student.group_id
                return f(*args, **kwargs)
                
        flash('У вас нет прав для доступа к этой странице', 'danger')
        return redirect(url_for('main.index'))
    return decorated_function 