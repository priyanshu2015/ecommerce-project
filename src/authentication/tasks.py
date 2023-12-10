from authentication.models import User
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
import logging
from celery import shared_task
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.utils import timezone

logger = logging.getLogger(__file__)


@shared_task(bind=True)
def send_verify_email_link(self, user_id):
    user = User.objects.get(id=user_id)
    subject = "Verify Email for your Account Verification on WonderShop"
    template = "auth/email/verify_email.html"
    context_data = {
        "host": settings.FRONTEND_HOST,
        "uid": urlsafe_base64_encode(force_bytes(user.id)),
        "token": account_activation_token.make_token(user=user),
        "protocol": settings.FRONTEND_PROTOCOL
    }
    print(context_data)
    try:
        # Utility.send_mail_via_sendgrid(
        #     user.email,
        #     subject,
        #     template,
        #     context_data
        # )
        logger.info(f"Successfully sent the email verify link to user with {user_id} user_id")
    except Exception:
        logger.error(f"Some error occurred while sending email verify link to user with {user_id} user_id", exc_info=True)
        
    
@shared_task(bind=True)
def delete_expired_tokens(self):
    OutstandingToken.objects.filter(expires_at__lt=timezone.now()).delete()