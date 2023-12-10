from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import logging
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework_simplejwt.token_blacklist.models import \
OutstandingToken, BlacklistedToken
from django.utils import timezone

logger = logger = logging.getLogger(__file__)

User = get_user_model()

@shared_task(bind=True)
def send_verify_email_link(self, user_id):
    user = User.objects.get(id=user_id)
    subject = "Verify Email for your Account Verification on WonderShop"
    template = "auth/email/verify_email.html"
    context_data = {
        "host": settings.FRONTEND_HOST,
        "uid": urlsafe_base64_encode(force_bytes(user_id)),
        "token": account_activation_token.make_token(user=user),
        "protocol": settings.FRONTEND_PROTOCOL
    }
    try:
        # Utility.send_mail_via_sendgrid(
        #     user.email,
        #     subject,
        #     template,
        #     context_data
        # )
        logger.info(f"Successfully sent email verification link to user with {user_id} user_id")
    except Exception:
        logger.error(f"Some error occurred in signup endpoint while sending email verify link to user with {user_id} user_id", exc_info=True)



@shared_task(bind=True)
def delete_expired_tokens():
    OutstandingToken.objects.filter(expires_at__lt=timezone.now()).delete()