from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings
from rest_framework_simplejwt.utils import (
    datetime_from_epoch,  # datetime_to_epoch, format_lazy,
)

User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )

        extra_kwargs = {
            "password": {"write_only": True},
            # added this validator, as its a model serializer, so it will automatically check the duplicates but I am handling that logic in view
            "email": {
                "validators": [
                    EmailValidator,
                ]
            },
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        lowercase_email = value.lower()
        # below query is not required as validate method of serializer takes care of email using filter of iexact as its a modelserializer
        # it is required only if you put extra_kwargs = {'email': {'validators': [EmailValidator,]},} or if you use this then you can add db validation in views also
        # if User.objects.filter(email__iexact=value).exists():
        #     raise serializers.ValidationError("Duplicate")
        return lowercase_email



class UserLoginSerializer(serializers.ModelSerializer):
    username_or_email = serializers.CharField(
        write_only=True
    )  # altough in meta it has been mentioned in extra_kwargs that write_only=True, but again mentioned here because while serializing model object to serializer in preparing response it gives error if not mentioned here since this field is not present in model

    class Meta:
        model = User
        fields = (
            "username_or_email",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_superuser",
        )
        read_only_fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_superuser",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "username_or_email": {"write_only": True},
        }

    def validated_username_or_email(self, value):
        lowercase_username_or_email = value.lower()
        return lowercase_username_or_email


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            # prev_refresh_token = attrs['refresh']
            # prev_refresh_token_payload = jwt.decode(
            #     prev_refresh_token,
            #     settings.SIMPLE_JWT['VERIFYING_KEY'],
            #     algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
            # )
            # Above decode is automatically done by Token class which is inherited by RefreshToken

            # this will do the validation that entered refresh_token is expired/blacklisted or not.
            refresh = RefreshToken(attrs["refresh"])
            # If above gives error that Token is BlackListed, this means same refresh token is used 2 times. This is the point to alarm user and revoke all previous decendent refresh_tokens
            # creates a new access token
            data = {"access": str(refresh.access_token)}

            if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
                payload = refresh.payload
                id = payload["user_id"]
                user = User.objects.get(id=id)
                # if user account is not active then can not get new refresh tokens and his refresh token will be of no use even before expiry if his account is not verified
                if not settings.ALLOW_NEW_REFRESH_TOKENS_FOR_UNVERIFIED_USERS:
                    if user.is_active == False:
                        raise TokenError(
                            {"detail": "User is inactive", "code": "user_inactive"}
                        )

                if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                    try:
                        # Attempt to blacklist the given refresh token
                        refresh.blacklist()  # make 3 db queries --> 1. get_or_create in OutstandingToken model(1 or 2 db queries) 2. get_or_create in BlacklistedToken model

                    except AttributeError:
                        # If blacklist app not installed, `blacklist` method will
                        # not be present
                        pass

                refresh.set_jti()
                refresh.set_exp()

                # Extra: Added new stuff in addition to normal default serializer
                if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                    # below 3 lines of code should be here but due to ALLOW_NEW_REFRESH_TOKENS_FOR_UNVERIFIED_USERS placing them above
                    # payload = refresh.payload
                    # user_uid = payload["user_id"]
                    # user = User.objects.get(user_uid=user_uid)
                    # refresh.for_user(user)
                    OutstandingToken.objects.create(
                        jti=payload[settings.SIMPLE_JWT["JTI_CLAIM"]],
                        # defaults={
                        #     "user_id":user.id,
                        #     "token":str(refresh),
                        #     "created_at":refresh.current_time,
                        #     "expires_at":datetime_from_epoch(payload['exp']),
                        # }
                        user=user,
                        token=str(refresh),
                        created_at=refresh.current_time,
                        expires_at=datetime_from_epoch(payload["exp"]),
                    )

                data["refresh"] = str(refresh)

            return data

        # TokenError raised by RefreshToken if token is blacklisted
        except TokenError as e:
            raise

        except serializers.ValidationError:
            raise

        except Exception:
            # print("Fatal Error While Logging In : \n" + traceback.format_exc())
            # raise serializers.ValidationError(
            #     "Fatal Error while generating a refresh token in serializers")
            raise


class UserLogoutSerializer(serializers.Serializer):
    all = serializers.BooleanField(required=False)
    refresh = serializers.CharField(required=False)

    class Meta:
        fields = (
            "all",
            "refresh",
        )

    def validate(self, attrs):
        all = attrs.get("all")
        refresh = attrs.get("refresh")
        if not all:  # all is empty or false
            if not refresh:
                raise serializers.ValidationError(
                    {
                        "refresh": "If logout from all devices then all parameter should be be passed with true else refresh is a required parameter to logout from the current device"
                    }
                )
        return super().validate(attrs)


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_verify = serializers.CharField()

    # def validate_old_password(self, value):
    #     if len(value)> 128:
    #         raise serializers.ValidationError("Password can't be more than 100 characters")
    #     return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_verify"):
            raise serializers.ValidationError(
                {"new_password_verify": "Password doesn't match"}
            )
        return super().validate(attrs)


class UserForgotPasswordSendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = "email"



class PasswordResetConfirmPostRequestSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    new_password_verify = serializers.CharField()

    # def validate_old_password(self, value):
    #     if len(value)> 128:
    #         raise serializers.ValidationError("Password can't be more than 100 characters")
    #     return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_verify"):
            raise serializers.ValidationError(
                {"new_password_verify": "Password doesn't match"}
            )
        return super().validate(attrs)