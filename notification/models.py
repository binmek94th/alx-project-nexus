import uuid

from django.db import models

from user.models import User


class Notification(models.Model):
    """
    This model represents a notification.
    It has fields user, message, is_read, created_at, updated_at and notification_type
    Each notification has a unique identifier, a reference to the receiver it belongs to,
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification_type = models.CharField(max_length=50, blank=True, null=True)
