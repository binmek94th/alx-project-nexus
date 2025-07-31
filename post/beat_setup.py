from django_celery_beat.models import IntervalSchedule

from utils.celery_beats import create_or_update_task


def create_periodic_task():
    """
    Create a periodic task to update expired stories.
    This task runs every minute and checks for stories that have expired.
    :return:
    """
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=5,
        period=IntervalSchedule.MINUTES,
    )
    create_or_update_task("Update Expired Stories", "post.tasks.delete_expired_stories", schedule)
