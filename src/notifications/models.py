from django.db import models
from django.contrib.postgres.fields import ArrayField
from common.models import TimeStampedModel
from django.contrib.auth import get_user_model

User = get_user_model()


class ScheduledNotification(TimeStampedModel):
    type_choices = (
        ("PUBLIC", "PUBLIC"),
        ("USER_SPECIFIC", "USER_SPECIFIC")
    )
    event_type_choices = (
        ("ORDER_UPDATE", "ORDER_UPDATE"),
        ("PROMOTIONAL", "PROMOTIONAL"),
        ("ANNOUNCEMENT", "ANNOUNCEMENT")
    )
    medium_choices = (
        ("PHONE_SMS", "PHONE_SMS"),
        ("EMAIL", "EMAIL"),
        ("PUSH_NOTIFICATION", "PUSH_NOTIFICATION"),
        ("APP_NOTIFICATION", "APP_NOTIFICATION"),
        ("WHATSAPP", "WHATSAPP")
    )
    status_choices = (
        ("PENDING", "PENDING"),
        ("SUCCESS", "SUCCESS")
    )

    type = models.CharField(choices=type_choices, max_length=16)
    user_ids = ArrayField(
        models.IntegerField(), default=list, null=True, blank=True
    )
    event_type = models.CharField(choices=event_type_choices, max_length=20)
    scheduled_at = models.DateTimeField()
    send_via = ArrayField(models.CharField(choices=medium_choices, max_length=20), default=list)
    # {"notifications": {"email": {"template": "", "service_provider": "sendgrid", "subject": "", "context_data": {}}}}
    status = models.CharField(choices=status_choices, max_length=16)
    extras = models.JSONField(default=dict)



class Notification(TimeStampedModel):
    event_type_choices = (
        ("ORDER_UPDATE", "ORDER_UPDATE"),
        ("PROMOTIONAL", "PROMOTIONAL"),
        ("ANNOUNCEMENT", "ANNOUNCEMENT")
    )
    medium_choices = (
        ("PHONE_SMS", "PHONE_SMS"),
        ("EMAIL", "EMAIL"),
        ("PUSH_NOTIFICATION", "PUSH_NOTIFICATION"),
        ("APP_NOTIFICATION", "APP_NOTIFICATION"),
        ("WHATSAPP", "WHATSAPP")
    )
    status_choices = (
        ("PENDING", "PENDING"),
        ("SUCCESS", "SUCCESS")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    reference = models.ForeignKey(ScheduledNotification, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(choices=event_type_choices, max_length=20)
    # sent_at will be populated, once its successfully sent
    sent_at = models.DateTimeField(blank=True, null=True)
    medium = models.CharField(choices=medium_choices, max_length=20)
    extras = models.JSONField(default=dict)
    status = models.CharField(choices=status_choices, max_length=16)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'reference', 'medium'], name='unique_user_notification'
            )
        ]
