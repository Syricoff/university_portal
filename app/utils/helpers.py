"""
Вспомогательные функции для приложения.
"""
from datetime import datetime, timedelta


def get_default_date_range(days=30):
    """
    Возвращает диапазон дат по умолчанию для фильтров.
    
    Args:
        days (int): Количество дней в диапазоне
        
    Returns:
        tuple: (start_date, end_date) в формате строк YYYY-MM-DD
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def calculate_attendance_percentage(presents, total):
    """
    Рассчитывает процент посещаемости.
    
    Args:
        presents (int): Количество присутствий
        total (int): Общее количество занятий
        
    Returns:
        float: Процент посещаемости (0-100)
    """
    if total == 0:
        return 0
    return (presents / total) * 100


def format_date(date_obj, format_str="%d.%m.%Y"):
    """
    Форматирует дату в строку.
    
    Args:
        date_obj (datetime.date): Объект даты
        format_str (str): Формат строки
        
    Returns:
        str: Отформатированная строка даты
    """
    if not date_obj:
        return ""
    return date_obj.strftime(format_str)


def parse_date(date_str, format_str="%Y-%m-%d"):
    """
    Преобразует строку в объект даты.
    
    Args:
        date_str (str): Строка с датой
        format_str (str): Формат строки
        
    Returns:
        datetime.date: Объект даты или None при ошибке
    """
    try:
        return datetime.strptime(date_str, format_str).date()
    except (ValueError, TypeError):
        return None 