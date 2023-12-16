from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsSuperUser
from notifications.choices import NotificationStatusChoice
from .serializers import ScheduleNotificationSerializer, ScheduleNotificationBaseSerializer, ScheduleNotificationRequestSerializer
from rest_framework.response import Response
from common.helpers import validation_error_handler
from rest_framework import status
from .models import ScheduledNotification
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import shortuuid
import json
from drf_yasg.utils import swagger_auto_schema


class ScheduleNotificationView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    request_serializer_class = ScheduleNotificationRequestSerializer
    response_serializer_class = ScheduleNotificationBaseSerializer
    
    @swagger_auto_schema(request_body=ScheduleNotificationRequestSerializer, responses={status.HTTP_200_OK: ScheduleNotificationBaseSerializer})
    def post(self, request, *args, **kwargs):
        request_data = request.data
        serializer = self.request_serializer_class(data=request_data)
        if serializer.is_valid() is False:
            return Response({
                "status": "error",
                "message": validation_error_handler(serializer.errors),
                "payload": {
                    "errors": serializer.errors
                }
            }, status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        scheduled_notification = ScheduledNotification.objects.create(
            status=NotificationStatusChoice.PENDING,
            **validated_data
        )
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=scheduled_notification.scheduled_at.hour,
            minute=scheduled_notification.scheduled_at.minute,
            day_of_month=scheduled_notification.scheduled_at.day,
            month_of_year=scheduled_notification.scheduled_at.month
        )
        uuid = shortuuid.uuid()
        task = PeriodicTask.objects.create(
            crontab=schedule, 
            name=f"notification_{uuid}",
            task="notifications.tasks.notification_mapper",
            one_off=True,
            args=json.dumps([scheduled_notification.id])
        )
        payload = ScheduleNotificationSerializer(scheduled_notification).data
        response_data = {
            "status": "success",
            "message": "Successfully created",
            "payload": payload
        }
        return Response(self.response_serializer_class(response_data).data, status=status.HTTP_200_OK)