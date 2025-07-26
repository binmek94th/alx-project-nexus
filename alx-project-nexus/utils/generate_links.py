from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from alx_project_nexus.settings import FRONTEND_URL


def generate_email_confirmation_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    link = f"{FRONTEND_URL}/auth/verify-email/?uid={uid}&token={token}"
    return link


def generate_password_reset_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    link = f"{FRONTEND_URL}/reset-password/?uid={uid}&token={token}"
    return link
