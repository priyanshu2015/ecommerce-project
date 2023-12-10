from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from notifications.serializers import ScheduleNotificationRequestSerializer, ScheduleNotificationBaseSerializer, ScheduleNotificationSerializer
from rest_framework.views import APIView
from common.permissions import IsSuperUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from common.helpers import validation_error_handler
from notifications.models import ScheduledNotification
from drf_yasg.utils import swagger_auto_schema
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone
import shortuuid
import json

from notifications.tasks import notification_mapper


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
        scheduled_notification = ScheduledNotification.objects.create(**validated_data)
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=scheduled_notification.scheduled_at.hour,
            minute=scheduled_notification.scheduled_at.minute,
            day_of_month=scheduled_notification.scheduled_at.day,
            month_of_year=scheduled_notification.scheduled_at.month
        )
        uuid = shortuuid.uuid()
        task = PeriodicTask.objects.create(crontab=schedule, name=f"notification_{uuid}", task='notifications.tasks.notification_mapper', one_off=True, args=json.dumps([scheduled_notification.id]))# kwargs={"id": scheduled_notification.id})
        # task.enabled = True
        # task.save()

        # countdown = scheduled_notification.scheduled_at.timestamp() - timezone.now().timestamp()
        # task = notification_mapper.apply_async(kwargs={"id": scheduled_notification.id}, countdown=countdown)

        payload = ScheduleNotificationSerializer(scheduled_notification).data

        response_data = {
            "status": "success",
            "message": "Successfully Created",
            "payload": payload
        }
        return Response(self.response_serializer_class(response_data).data, status=status.HTTP_200_OK)
