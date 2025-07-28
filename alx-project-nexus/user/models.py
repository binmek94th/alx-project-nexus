import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class PrivacyChoice(models.TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True, db_index=True)
    privacy_choice = models.CharField(
        max_length=10,
        choices=PrivacyChoice.choices,
        default=PrivacyChoice.PUBLIC
    )

    def __str__(self):
        return self.username + " " + self.privacy_choice


class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', null=True, blank=True)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class FollowRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_follow_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_follow_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sender', 'receiver')
