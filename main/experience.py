from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import WorkExperienceForm
from users.models import *
from vacancies.models import *


def calculate_and_save_work_experience(work_experience, request):
    if work_experience.date_started:
        if work_experience.currently_working:
            delta = timezone.now().date() - work_experience.date_started
        elif work_experience.date_ended:
            delta = work_experience.date_ended - work_experience.date_started
        else:
            return False  # Invalid scenario
        years = delta.days // 365
        months = (delta.days % 365) // 30
        work_experience.years = years
        work_experience.months = months
    work_experience.user = request.user
    work_experience.save()
    return True
