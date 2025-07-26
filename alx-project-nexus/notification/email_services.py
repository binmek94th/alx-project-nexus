from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError

from alx_project_nexus import settings
from .serializers import EmailSerializer
from utils.redis_client import redis_client
from .tasks import send_email

EMAIL_RATE_LIMIT_KEY = "email_rate:{email}{type}"
EMAIL_RATE_LIMIT_MAX = settings.EMAIL_RATE_LIMIT_MAX
EMAIL_RATE_LIMIT_WINDOW = settings.EMAIL_RATE_LIMIT_WINDOW
FRONTEND_URL = settings.FRONTEND_URL

email_mapping = {
    "welcome": {"html": "emails/welcome.html", "text": "emails/welcome.txt"},
    "password_reset": {"html": "emails/reset_password.html", "text": "emails/reset_password.txt"},
    "password_changed": {"html": "emails/password_reset_confirmation.html", "text": "emails"
                                                                                    "/password_reset_confirmation.txt"},
    "email_verification": {"html": "emails/verification.html", "text": "emails/verification.txt"},
}


def send_email_service(data):
    """
    Send email service function to handle email sending with rate limiting. This function validates the input data
    using the EmailSerializer, checks the rate limit for the email type and recipient, and sends the email if valid.
    It uses a Redis client to manage rate limiting and Celery to handle the email sending asynchronously. The email
    templates are defined in the email_mapping dictionary, which maps email types to their respective HTML and text
    templates.
    :param data: :return:
    """
    serializer = EmailSerializer(data=data)

    if serializer.is_valid():
        email_type = serializer.validated_data.get('email_type')
        recipient_list = serializer.validated_data.get('recipient_list')
        subject = serializer.validated_data.get('subject', 'No Subject')
        context = serializer.validated_data.get('context', {})

        rate_key = EMAIL_RATE_LIMIT_KEY.format(email=recipient_list[0], type=email_type)

        count = redis_client.incr(rate_key)

        if count == 1:
            redis_client.expire(rate_key, EMAIL_RATE_LIMIT_WINDOW)

        if count > EMAIL_RATE_LIMIT_MAX:
            raise ValidationError({"rate_limit": "Rate limit exceeded. Please try again later."})

        email_template = email_mapping.get(email_type)
        if not email_template:
            raise ValidationError({"email_template": "Email template not found."})

        message_html = render_to_string(email_template['html'], context)
        message_plain = render_to_string(email_template['text'], context)

        send_email.delay(subject, message_plain, message_html, recipient_list)

    return serializer
