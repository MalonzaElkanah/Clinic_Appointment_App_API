from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework.exceptions import APIException

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

def MySendEmail(subject, template, data, recipients, from_email=None):
    if from_email == None:from_email=DEFAULT_FROM_EMAIL
    rendered = render_to_string(template, data)
    # print("Sending email...")
    ema = send_mail(
        subject=subject,
        message="",
        html_message=rendered,
        from_email=from_email,
        recipient_list=recipients,  # ['micha@sisitech.com'],
        fail_silently=False,
        # reply_to="room@katanawebworld.com"
    )
    return ema



class MyCustomException(APIException):
    status_code = 503
    detail = "Service temporarily unavailable, try again later."
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

    def __init__(self, message, code=400):
        self.status_code = code
        self.default_detail = message
        self.detail = message
