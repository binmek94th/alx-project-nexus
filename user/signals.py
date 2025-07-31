from django.db.models import signals
from django.dispatch import receiver

from notification.tasks import create_notification
from user.models import Follow, FollowRequest


@receiver(signals.post_save, sender=Follow)
def send_followed_notification(sender, instance, created, **kwargs):
    if created:
        create_notification.delay(instance.following.id, f"{instance.follower.username} has started following you",
                                  "Follow Notification")


@receiver(signals.post_save, sender=FollowRequest)
def send_follow_request_notification(sender, instance, created, **kwargs):
    if created:
        create_notification.delay(instance.receiver.id, f"{instance.sender.username} has requested to follow you",
                                  "Follow Request")
