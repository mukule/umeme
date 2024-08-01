# utils.py
from datetime import datetime


def calculate_experience(start_date, end_date=None):
    if end_date is None:
        end_date = datetime.now().date()
    delta = end_date - start_date
    years = delta.days // 365
    months = (delta.days % 365) // 30
    return years, months
