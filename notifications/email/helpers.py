from club.settings import UNISENDER_API_KEY

import requests

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

    def send(self):
        ''' semd email '''
        request_body = {
            "message": {
                "recipients": [
                    {
                        "email": self.email,
                    }
                ],
                "from_email": "club@sorokin.club" ,
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
