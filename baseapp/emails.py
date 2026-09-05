import resend
from django.template.loader import render_to_string
from core.settings import RESEND_API_KEY

resend.api_key = RESEND_API_KEY


def send_verification_code(user_email, code):
    html = render_to_string('emails/verification_code.html', {
        'user_email': user_email,
        'code': code,
    })

    params: resend.Emails.SendParams = {
    "from": "Your Resume <noreply@curiosite.uz>",
    "to": [user_email],
    "subject": "Verification code",
    "html": html
    }

    email = resend.Emails.send(params)