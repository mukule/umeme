from datetime import date
from users.models import WorkExperience


def calculate_total_work_experience(user):
    """
    Calculate and return the total work experience for a given user in years and months.
    """
    total_years = 0
    total_months = 0

    # Fetch all work experiences related to the user
    work_experiences = WorkExperience.objects.filter(user=user)

    for experience in work_experiences:
        if experience.currently_working:
            end_date = date.today()
        else:
            end_date = experience.date_ended

        if experience.date_started and end_date:
            start_year, start_month = experience.date_started.year, experience.date_started.month
            end_year, end_month = end_date.year, end_date.month

            # Calculate difference in years and months
            year_diff = end_year - start_year
            month_diff = end_month - start_month

            if month_diff < 0:
                year_diff -= 1
                month_diff += 12

            total_years += year_diff
            total_months += month_diff

    # Convert total months to years and months
    additional_years, remaining_months = divmod(total_months, 12)
    total_years += additional_years

    experience = f"{total_years} years {remaining_months} months"
    return experience
