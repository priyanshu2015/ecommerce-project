from django.contrib import admin
from .models import Notification, ScheduledNotification

# Register your models here.
admin.site.register(ScheduledNotification)
admin.site.register(Notification)