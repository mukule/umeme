from datetime import date


def calculate_work_experience(work_experiences):
    total_years = 0
    total_months = 0

    for experience in work_experiences:
        if experience.currently_working:
            end_date = date.today()
        else:
            end_date = experience.date_ended

        if experience.date_started and end_date:
            delta = end_date - experience.date_started
            months = delta.days // 30
            years = months // 12
            months = months % 12

            total_years += years
            total_months += months

    total_years += total_months // 12
    total_months = total_months % 12

    return total_years, total_months
