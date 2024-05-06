from .models import Application, Resume, WorkExperience, Certification
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import *
from django.db.models import Q
from users.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.html import format_html
from .work_experience import calculate_work_experience
from .checks import *
from django.utils import timezone


def check_user_qualifications(request, user, vacancy):
    # Check basic education and resume
    if not check_basic_education_and_resume(user):
        messages.error(
            request, 'Update your Basic information / academic Details to apply !!')
        return False

    # Check certifications
    if not check_certifications(user, vacancy):
        messages.error(
            request, 'Certifications are required for this position')
        return False

    # Check college education
    if not check_college_education(user, vacancy):
        messages.error(
            request, 'College/Further studies are required for this position')
        return False

    # Check membership
    if not check_membership(user, vacancy):
        messages.error(
            request, 'Professional Membership required for this position')
        return False

    # Check referee count
    if not check_referee_count(user):
        messages.error(
            request, 'You don\'t have enough referees to apply. 3 referees are required.')
        return False

    return True


def check_qualifications(request, vacancy, user, total_work_experience_years, total_work_experience_months):
    user_resume = get_object_or_404(Resume, user=user)
    min_educational_level = vacancy.min_educational_level
    user_educational_level = user_resume.educational_level

    qualify_educational_level = user_educational_level.index == min_educational_level.index
    qualify_work_experience = (total_work_experience_years * 12) + \
        total_work_experience_months >= vacancy.min_work_experience

    disqualification_reason = ""
    if not qualify_educational_level and not qualify_work_experience:
        disqualification_reason = "Does not meet required education level and work experience"
    elif not qualify_educational_level:
        disqualification_reason = "Does not meet required education level"
    elif not qualify_work_experience:
        disqualification_reason = "Does not meet work experience"

    if disqualification_reason:
        messages.error(request, disqualification_reason)
        return False

    return True
