from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from .models import ScheduledNotification
from django.dispatch import receiver
import shortuuid
import json
from django_celery_beat.models import PeriodicTask, CrontabSchedule


@receiver(post_save, sender=ScheduledNotification)
def create_backround_task(sender, instance, created, **kwargs):
    if created:
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=instance.scheduled_at.hour,
            minute=instance.scheduled_at.minute,
            day_of_month=instance.scheduled_at.day,
            month_of_year=instance.scheduled_at.month
        )
        uuid = shortuuid.uuid()
        task = PeriodicTask.objects.create(
            crontab=schedule, 
            name=f"notification_{uuid}",
            task="notifications.tasks.notification_mapper",
            one_off=True,
            args=json.dumps([instance.id])
        )