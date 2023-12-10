from notifications.models import ScheduledNotification
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Notification
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()


def send_notification():
    pass


def notification_sender():
    time_threshold = timezone.now() - timedelta(minutes=10)
    # TODO: Add Pagination
    notifications = Notification.objects.filter(
        created_at__lte=time_threshold,
        status="PENDING"
    )
    for notification in notifications:
        if notification.medium == "EMAIL":
            # send notification via email
            notification.status = "SUCCESS"
            notification.save()
        elif notification.medium == "PUSH_NOTIFICATION":
            pass



def notification_mapper(self, id):
    scheduled_notification = ScheduledNotification.objects.filter(
        id=id,
        status="PENDING"
    ).select_for_update(nowait=True)
    # TODO: Add Pagination
    if scheduled_notification.type == "USER_SPECIFIC":
        pending_users = User.objects.filter(id__in=scheduled_notification.user_ids).exclude(notifications__reference_id=scheduled_notification.id)
    elif scheduled_notification.type == "PUBLIC":
        pending_users = User.objects.all().exclude(notifications__reference_id=scheduled_notification.id)
    if pending_users.count() == 0:
        scheduled_notification.status = "SUCCESS"
        scheduled_notification.save()
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


def notification_scheduler():
    time_threshold = timezone.now() - timedelta(minutes=30)
    # TODO: Add Pagination
    scheduled_notifications = ScheduledNotification.objects.filter(
        scheduled_at__lte=time_threshold,
        status__in=["PENDING", "IN_PROGRESS"]
    )
    for scheduled_notification in scheduled_notifications:
        notification_mapper.delay()