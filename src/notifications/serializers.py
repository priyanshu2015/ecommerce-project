from rest_framework import serializers
from .models import ScheduledNotification


class ScheduleNotificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledNotification
        fields = [
            "type",
            "user_ids",
            "event_type",
            "scheduled_at",
            "send_via"
        ]


class ScheduleNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledNotification
        fields = "__all__"



class ScheduleNotificationBaseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    payload = ScheduleNotificationSerializer()