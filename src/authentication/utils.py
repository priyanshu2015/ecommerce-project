import shortuuid
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthUtility:
    # method that creates username using email
    @staticmethod
    def create_username(email):
        try:
            total_retries = 5
            email_split = email.rsplit(
                "@", 1
            )
            email_part = email_split[0][0:20]
            clean_email_part = "".join(char for char in email_part if char.isalnum())
            for i in range(0, total_retries):
                uuid = shortuuid.uuid()  # returns a 22 length alphanumeric string
                username = (
                    f"{clean_email_part}_{uuid}".lower()
                )  # this is done to render username to frontend in lowercase, store in db in lowercase always and prvent using iexact in db query
                user = User.objects.filter(username=username)
                if user.exists():
                    continue
                else:
                    return username
            raise Exception("Max retries done for creating a new username.")
        except Exception as e:
            raise Exception("Error while creating a new username") from e

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
