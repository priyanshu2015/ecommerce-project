from django.contrib import admin
from notifications.models import ScheduledNotification, Notification

# Register your models here.
admin.site.register(ScheduledNotification)
admin.site.register(Notification)