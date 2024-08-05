from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import BadHeaderError
from django.core.exceptions import ImproperlyConfigured
import logging

# Setup logging
logger = logging.getLogger(__name__)


def send_custom_email(subject, message, send_to, cc=None, bcc=None, html_message=None):
    """
    Send an email.

    :param subject: Subject of the email
    :param message: Plain text message of the email
    :param send_to: List of recipient email addresses
    :param cc: List of cc email addresses (default is None)
    :param bcc: List of bcc email addresses (default is None)
    :param html_message: HTML message of the email (default is None)
    :return: True if the email was sent successfully, False otherwise
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    default_bcc_emails = settings.BCC_EMAILS or []

    combined_bcc = default_bcc_emails + (bcc or [])

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=send_to,
        cc=cc,
        bcc=combined_bcc,
    )

    if html_message:
        email.attach_alternative(html_message, "text/html")

    try:
        email.send()
        return True
    except (BadHeaderError, ImproperlyConfigured) as e:

        logger.error(f"Email sending failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while sending email: {e}")
        return False
