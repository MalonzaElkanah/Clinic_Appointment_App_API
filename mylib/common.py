from django.core.mail import send_mail
from django.conf import settings

from rest_framework.exceptions import APIException

from dotenv import load_dotenv
import os


load_dotenv(os.path.join(settings.BASE_DIR, '.env'))


def MySendEmail(subject, message, recipients, from_email=None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    print("Sending email...\n\n")
    print(f"From: <{from_email}>")
    print(f"To: <{recipients}>\n")
    print(f"Subject: {subject}\n")
    print(message)

    email = send_mail(
        subject=subject,
        message=message,
        # html_message=rendered,
        from_email=from_email,
        recipient_list=recipients,
        fail_silently=False,
    )

    return email


class MyCustomException(APIException):
    status_code = 503
    detail = "Service temporarily unavailable, try again later."
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

    def __init__(self, message, code=400):
        self.status_code = code
        self.default_detail = message
        self.detail = message
