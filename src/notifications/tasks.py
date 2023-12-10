from celery import shared_task
from .models import ScheduledNotification, Notification
from .choices import NotificationTypeChoice, NotificationStatusChoice, MediumChoice
from authentication.models import User
from django.db import transaction
from django.utils import timezone
from datetime import timedelta


@shared_task(bind=True)
def notification_mapper(self, id):
    scheduled_notification = ScheduledNotification.objects.filter(
        id=id,
        status="PENDING"
    )
    if scheduled_notification.type == NotificationTypeChoice.USER_SPECIFIC:
        pending_users = User.objects.filter(id__in=scheduled_notification.user_ids).exclude(notifications__reference_id=scheduled_notification.id)
    elif scheduled_notification.type == NotificationTypeChoice.PUBLIC:
        pending_users = User.objects.all().exclude(notifications__reference_id=scheduled_notification.id)
    if pending_users.count() == 0:
        scheduled_notification.status = NotificationStatusChoice.SUCCESS
        scheduled_notification.save()
        return
    # TODO: make batches of lets say 1000 => and then create the notification object in another child task which you can trigger via delay
    for user in pending_users:
        with transaction.atomic():
            for medium in scheduled_notification.send_via:
                notification = Notification.objects.create(
                    user=user,
                    reference=scheduled_notification,
                    event_type=scheduled_notification.event_type,
                    status="PENDING",
                    medium=medium
                )
                
                
@shared_task(bind=True)
def notification_sender(self):
    notifications = Notification.objects.filter(
        status=NotificationStatusChoice.PENDING
    )
    for notification in notifications:
        if notification.medium == MediumChoice.EMAIL:
            # send the notification via email
            notification.status = NotificationStatusChoice.SUCCESS
            notification.save()
        elif notification.medium == MediumChoice.PUSH_NOTIFICATION:
            # make handler for this
            notification.status = NotificationStatusChoice.SUCCESS
            notification.save()


@shared_task(bind=True)
def notification_scheduler(self):
    time_threshold = timezone.now() - timedelta(minutes=30)
    scheduled_notifications = ScheduledNotification.objects.filter(
        scheduled_at__lte=time_threshold,
        status=NotificationStatusChoice.PENDING
    )
    for notification in scheduled_notifications:
        notification_mapper.delay(id=notification.id)
    
                
