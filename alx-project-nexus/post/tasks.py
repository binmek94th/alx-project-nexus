from celery import shared_task
from django.utils import timezone

from post.models import Story


@shared_task
def delete_expired_stories():
    """
    Task to delete expired stories.
    This task checks for stories that have expired based on their `expires_at` field.
    If a story's `expires_at` is less than or equal to the current time,
    it marks the story as expired by setting `is_expired` to True and saves the story.
    This task is intended to be run periodically to ensure that expired stories are handled appropriately.
    :return:
    """
    now = timezone.now()
    expired = Story.objects.filter(expires_at__lte=now)
    for story in expired:
        story.is_expired = True
        story.save()
