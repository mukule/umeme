# application_utils.py

from django.shortcuts import get_object_or_404
from .models import Application, Resume
from .work_experience import calculate_work_experience
from .checks import *


def create_application(vacancy, user, total_work_experience_years, total_work_experience_months,
                       qualify_educational_level, qualify_work_experience, disqualification_reason):
    user_resume = get_object_or_404(Resume, user=user)
    user_educational_level = user_resume.educational_level
    application = Application.objects.create(
        applicant=user,
        vacancy=vacancy,
        highest_educational_level=user_educational_level.name,
        work_experience=total_work_experience_years,
        months=total_work_experience_months,
        qualify=qualify_educational_level and qualify_work_experience,
        disqualification_reason=disqualification_reason,
    )

    application.reference_number = f"{vacancy.ref}/{application.index}"
    application.save()
    return application
