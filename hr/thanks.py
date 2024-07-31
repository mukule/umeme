from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from vacancies.models import *
from .mails import *


def send_emails_to_applicants(vacancy):
    """
    Send emails to all applicants of a specific vacancy when it is closed.

    :param vacancy: The vacancy instance
    """
    thanks_message_instance = ThanksMessage.objects.first()
    if thanks_message_instance:
        thanks_message = thanks_message_instance.message
        applications = Application.objects.filter(
            vacancy=vacancy, shortlisted=True)
        send_to = [application.applicant.email for application in applications]

        if send_to:
            subject = f"Update on Your Application for {vacancy.title}"

            send_custom_email(subject, thanks_message, send_to)
            print(f"Emails sent to {len(send_to)} applicants.")
        else:
            print("No applicants found for this vacancy.")
    else:
        print("Thanks message does not exist.")
