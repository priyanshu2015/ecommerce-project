from django.db import models
from common.models import TimeStampedModel
from .choices import NotificationTypeChoice, EventTypeChoice, NotificationStatusChoice, MediumChoice
from django.contrib.postgres.fields import ArrayField
from authentication.models import User

class ScheduledNotification(TimeStampedModel):
    type = models.CharField(choices=NotificationTypeChoice.CHOICE_LIST, max_length=16)
    user_ids = ArrayField(models.IntegerField(), default=list, blank=True, null=True)
    event_type = models.CharField(choices=EventTypeChoice.CHOICE_LIST, max_length=20)
    send_via = ArrayField(models.CharField(choices=MediumChoice.CHOICE_LIST, max_length=20), default=list)
    status = models.CharField(choices=NotificationStatusChoice.CHOICE_LIST, max_length=16)
    scheduled_at = models.DateTimeField()
    # email
    # extras = {"notifications": {"email": {"template": "", "service_provider": "sendgrid", "subject": "", "context_data": {}}}}
    extras = models.JSONField(default=dict)
    
    
class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    reference = models.ForeignKey(ScheduledNotification, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(choices=EventTypeChoice.CHOICE_LIST, max_length=20)
    sent_at = models.DateTimeField(blank=True, null=True)
    medium = models.CharField(choices=MediumChoice.CHOICE_LIST, max_length=20)
    extras = models.JSONField(default=dict)
    status = models.CharField(choices=NotificationStatusChoice.CHOICE_LIST, max_length=16)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["user", "reference", "medium"], name="unique_user_notification"
            )
        ]
    