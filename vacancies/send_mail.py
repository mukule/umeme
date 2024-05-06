
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


def send_application_email(application, vacancy, user):
    mail_subject = f"Application successful for {vacancy.title}"
    user_message = format_html(
        "Thank you for applying for the {} position. Your application reference number is {}. Note that only shortlisted applicants will be contacted.",
        vacancy.title,
        application.reference_number
    )
    user_email = EmailMessage(mail_subject, user_message, to=[user.email])
    user_email.send()
