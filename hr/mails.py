from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


def send_custom_email(subject, message, send_to, cc=None, bcc=None, html_message=None):
    """
    Send an email.

    :param subject: Subject of the email
    :param message: Plain text message of the email
    :param send_to: List of recipient email addresses
    :param cc: List of cc email addresses (default is None)
    :param bcc: List of bcc email addresses (default is None)
    :param html_message: HTML message of the email (default is None)
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=send_to,
        cc=cc,
        bcc=bcc,
    )

    if html_message:
        email.attach_alternative(html_message, "text/html")

    email.send()
