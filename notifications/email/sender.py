# Django imports
from django.conf import settings

# imports for email
from django.core.mail import send_mail
from premailer import Premailer

# import config data
from club.settings import UNISENDER_API_KEY
from club.settings import APP_HOST

# Python import
import logging
import re
import requests

log = logging.getLogger(__name__)


class Email:
    ''' to prepare data for request and send email to user by Unisender'''
    headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-API-KEY': UNISENDER_API_KEY
            }
    base_url = 'https://go1.unisender.ru/ru/transactional/api/v1/email/send.json'

    def __init__(self, html, email, subject):
        ''' initialize instance '''
        self.html = html
        self.email = email
        self.subject = subject

    def prepare_email(self):
        ''' prepare HTML for email '''
        self.html = Premailer(
            html=self.html,
            base_url=APP_HOST,
            strip_important=False,
            keep_style_tags=True,
            capitalize_float_margin=True,
            cssutils_logging_level=logging.CRITICAL,
        ).transform()
        if "<!doctype" not in self.html:
            self.html = f"<!doctype html>{self.html}"
        return self.html

    def send(self):
        ''' send email '''
        log.info(f"Sending email to {recipient}")
        request_body = {
            "message": {
                "recipients": [
                    {
                        "email": self.email,
                    }
                ],
                "from_email": "club@sorokin.club",
                "from_name": "sorokin.club", 
                "body": {
                    "html": self.html,
                    "plaintext": "Hello"
                },
                "subject": self.subject
            }
        }
        requests.post(
            url=self.base_url,  
            json=request_body,
            headers=self.headers
        )


def send_club_email(recipient, subject, html, tags=None):
    log.info(f"Sending email to {recipient}")
    return None
#    prepared_html = prepare_letter(html, base_url=settings.APP_HOST)
#    return send_mail(
#        subject=subject,
#        html_message=prepared_html,
#        message=re.sub(r"<[^>]+>", "", prepared_html),
#        from_email=settings.DEFAULT_FROM_EMAIL,
#        recipient_list=[recipient],
#    )
