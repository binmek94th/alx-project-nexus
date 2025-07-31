from django.db.models import signals
from django.dispatch import receiver

from notification.tasks import create_notification
from post.models import Like, StoryLike, Comment


@receiver(signals.post_save, sender=Like)
def send_like_notification(sender, instance, created, **kwargs):
    if created:
        create_notification.delay(instance.post.author.id, f"{instance.user.username} liked your post",
                                  "Like Notification")


@receiver(signals.post_save, sender=StoryLike)
def send_like_notification(sender, instance, created, **kwargs):
    if created:
        create_notification.delay(instance.story.author.id, f"{instance.user.username} liked your story",
                                  "Like Notification")


@receiver(signals.post_save, sender=Comment)
def send_like_notification(sender, instance, created, **kwargs):
    if created:
        create_notification.delay(instance.post.author.id, f"{instance.user.username} commented in your post",
                                  "Comment Notification")
