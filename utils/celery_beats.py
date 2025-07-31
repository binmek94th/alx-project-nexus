from django_celery_beat.models import PeriodicTask


def create_or_update_task(name, task_name, schedule):
    task, created = PeriodicTask.objects.get_or_create(
        name=name,
        defaults={
            'task': task_name,
            'interval': schedule,
            'enabled': True,
        }
    )
    if not created:
        task.task = task_name
        task.interval = schedule
        task.enabled = True
        task.save()
    return task