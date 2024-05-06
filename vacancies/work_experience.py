from vacancies.models import *
from users.models import *


def calculate_work_experience(user_work_experience):
    if user_work_experience is None:
        return 0, 0

    if not hasattr(user_work_experience, '__iter__'):
        return 0, 0

    total_work_experience_years = sum(
        experience.years for experience in user_work_experience if experience.years is not None)
    total_work_experience_months = sum(
        experience.months for experience in user_work_experience if experience.months is not None)

    return total_work_experience_years, total_work_experience_months
