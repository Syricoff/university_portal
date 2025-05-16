"""
Основные маршруты приложения.
"""
from flask import Blueprint, redirect, url_for

# Создаем Blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Главная страница - перенаправление на список посещаемости.
    
    Returns:
        Redirect: Перенаправление на страницу списка посещаемости
    """
    return redirect(url_for('attendance.list')) 