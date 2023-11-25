from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.template.loader import get_template
from django.conf import settings
import logging

logger = logging.getLogger(__file__)


class Utility:
    @staticmethod
    def send_mail_via_sendgrid(
        to_email, subject, template, context_data, attachment=None
    ):
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=get_template(template).render(context_data),
        )
        if attachment is not None:
            message.add_attachment(attachment)
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            response_data = {
                "status_code": response.status_code,
                "body": response.body,
                "headers": response.headers,
            }
            logger.info(
                f"Response from Sendgrid while sending email with Subject: {subject} to user with {to_email} email address",
                extra={"data": response_data},
            )

        except Exception as e:
            raise Exception(
                f"failed to send email via Sendgrid with Subject: {subject} to user with {to_email} email address"
            ) from e
