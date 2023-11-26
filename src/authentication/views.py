from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from authentication.serializers import CreateUserSerializer, CustomTokenRefreshSerializer, PasswordResetConfirmPostRequestSerializer, UserChangePasswordSerializer, UserForgotPasswordSendEmailSerializer, UserLoginSerializer, UserLogoutSerializer
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from common.helpers import validation_error_handler
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import AuthUtility
from common.utils import Utility
from .tokens import account_activation_token
from django.contrib.auth.hashers import check_password
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from common.error_codes import ErrorCode

logger = logging.getLogger(__file__)

User = get_user_model()

# serializer_class
# different serializer for different request method
# different request, response serializer for one request method

class SignupView(APIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid() is False:
            errors = serializer.errors
            return Response({
                "status": "error",
                "message": validation_error_handler(errors),
                "payload": {
                    "errors": errors
                },
            }, status=status.HTTP_200_OK)
        validated_data = serializer.validated_data
        email = validated_data.get("email")
        # checking if user already exists or not in db with this email [as this check is removed from serializer]
        existing_user = User.objects.filter(email=email).first()
        if existing_user is not None:
            # - check if user account is active or not
            # - if its not active then send verification mail again as this might happen in following cases
            # - 1. user didn't got the mail for the first time and again try to hit the signup endpoint
            # - 2. user forgot to verify mail and after long time comes again
            # - 3. some malicious user tried to create an account on others behalf and failed to verify mail and then the real user comes to signup
            if existing_user.is_active == False:
                password = validated_data.get("password")
                existing_user.set_password(password)
                existing_user.save()
                user = existing_user
            else:
                logger.error(
                    "Account with this email already exists", exc_info=True
                )
                return Response(
                    {
                        "status": "error",
                        "message": "Account with this email already exists",
                        "payload": {
                            "email": ["Account with this email already exists"]
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # creating username(unique field in User model)
            username = AuthUtility.create_username(email)
            user = User.objects.create_user(
                username=username, is_active=False, **validated_data
            )

        # again serializing for creating response data
        serializer_data = self.serializer_class(existing_user)

        # send email
        subject = "Verify Email for Your Account Verification on WonderShop"
        template = "auth/email/verify_email.html"
        context_data = {
            # "username": existing_user.username,
            "host": settings.FRONTEND_HOST,
            "uid": urlsafe_base64_encode(
                force_bytes(user.id)
            ),
            "token": account_activation_token.make_token(user),
            "protocol": settings.FRONTEND_PROTOCOL,
        }
        print(context_data)
        try:
            # Utility.send_mail_via_sendgrid(
            #     user.email, subject, template, context_data
            # )
            return Response(
                data={
                    "status": "success",
                    "message": "Sent the account verification link on your email address",
                    "payload": {
                        **serializer_data.data,
                        "token": AuthUtility.get_tokens_for_user(user),
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception:
            logger.error(
                "Error while sending mail for account verification due to sendgrid",
                exc_info=True,
            )
            return Response(
                {
                    "status": "error",
                    "message": "Error while sending mail for account verification",
                    "payload": {},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({
                "status": "success",
                "message": "Successfully Verified",
                "payload": ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Activation link is invalid!",
                "payload": {}
            }, status=status.HTTP_403_FORBIDDEN)


class LoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid() is False:
            # converting email or username to lowercase is done by serializer
            return Response(
                data={
                    "status": "error",
                    "message": validation_error_handler(serializer.errors),
                    "payload": {
                        "errors": serializer.errors,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        validated_data = serializer.validated_data
        user = (
            User.objects.filter(
                email=validated_data.get("username_or_email")
            ).first()
            or User.objects.filter(
                username=validated_data.get("username_or_email")
            ).first()
        )
        if user is not None:
            # credentials = {
            #     'email':user.email,
            #     'password': validated_data.get("password")
            # }
            # if all(credentials.values()):
            #     # the below authenticate function will cause an extra db query although we have got the user above itself
            #     user = authenticate(**credentials)

            # INFO: validating password by our own using check_password in order to reduce redundant db query by authenticate
            validate_password = check_password(
                validated_data.get("password"), user.password
            )
            if validate_password:
                if not user.is_active:
                    return Response(
                        {
                            "status": "error",
                            "message": "User account is not active, Please verify your email or do the Sign Up again",
                            "payload": "",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                # context is needed to generate hyperlinks
                serializer_data = self.serializer_class(
                    user, context={"request": request}
                )
                return Response(
                    {
                        "status": "success",
                        "message": "Login Successful",
                        "payload": {
                            **serializer_data.data,
                            "token": AuthUtility.get_tokens_for_user(user)
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {
                        "status": "error",
                        "message": "Unable to log in with the provided credentials",
                        "payload": "",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "No user found with the provided credentials",
                    "payload": "",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    # For drf_yasg integration with restframework_simplejwt
    # @swagger_auto_schema(responses={status.HTTP_200_OK: TokenRefreshResponseSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserLogoutView(GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        logger.info(
            "incoming request data for user logout", extra={"data": request_data}
        )
        serialized = self.serializer_class(data=request_data)

        if serialized.is_valid():
            try:
                validated_data = serialized.validated_data
                if validated_data.get("all"):
                    token: OutstandingToken
                    for token in OutstandingToken.objects.filter(user=request.user):
                        _, _ = BlacklistedToken.objects.get_or_create(token=token)
                        # print(token)
                    return Response(
                        data={
                            "status": "sucess",
                            # All refresh tokens are blacklisted
                            "message": "Successfully logged out from all devices",
                            "payload": "",
                        },
                        status=status.HTTP_200_OK,
                    )
                refresh_token = validated_data.get("refresh")
                token = RefreshToken(token=refresh_token)
                token.blacklist()
                return Response(
                    data={
                        "status": "sucess",
                        "message": "Successfully logged out",  # Only sent refresh token is blacklisted
                        "payload": "",
                    },
                    status=status.HTTP_200_OK,
                )
            except TokenError:
                return Response({"detail": "Token is blacklisted", "code": "token_not_valid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        else:
            return Response(
                data={
                    "status": "error",
                    "message": "Error in input data",
                    "payload": serialized.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserChangePasswordView(GenericAPIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_data = request.data
        serialized = self.serializer_class(data=request_data)
        if serialized.is_valid():
            user = request.user
            validated_data = serialized.validated_data
            validate_password = user.check_password(
                validated_data.get("old_password")
            )
            if validate_password:
                user.set_password(validated_data.get("new_password"))
                user.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Password has been changed successfully",
                        "payload": "",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": "error",
                        "message": "Old password didn't match",
                        "payload": {
                            "old_password": [
                                "Old password didn't match with the existing password of the user"
                            ]
                        },
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        else:
            return Response(
                data={
                    "status": "error",
                    "message": validation_error_handler(serialized.errors),
                    "payload": {
                        "errors": serialized.errors,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserForgotPasswordSendEmailView(GenericAPIView):
    serializer_class = UserForgotPasswordSendEmailSerializer
    throttle_scope = 'send_email'

    def post(self, request, *args, **kwargs):
        try:
            request_data = request.data
            logger.info(
                "incoming request data for user forgot password send email",
                extra={"data": request_data},
            )
            serialized = self.serializer_class(data=request_data)
            if serialized.is_valid():
                validated_data = serialized.validated_data
                existing_user = User.objects.filter(
                    email=validated_data.get("email")
                ).first()
                if existing_user:
                    if existing_user.is_active == False:
                        return Response(
                            data={
                                "status": "error",
                                "message": "Your account is not verified yet",
                                "payload": {
                                    "email": [
                                        "Your account is not verified yet, Please verify your email first. In case the verification link is expired or lost, Try to Sign Up again."
                                    ]
                                },
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    subject = "Letsprogramify Password Reset"
                    template = "users/email/forgot_password.html"
                    token_generator = PasswordResetTokenGenerator()
                    context_data = {
                        # "username": existing_user.username,
                        "host": settings.FRONTEND_HOST,
                        "uid": urlsafe_base64_encode(
                            force_bytes(existing_user.user_uid)
                        ),
                        "token": token_generator.make_token(existing_user),
                        "protocol": settings.FRONTEND_PROTOCOL,
                    }
                    try:
                        Utility.send_mail_via_sendgrid(
                            existing_user.email, subject, template, context_data
                        )
                        return Response(
                            {
                                "status": "success",
                                "message": "Successfully sent the change password link on your email address, Wait 30 seconds to resend",
                                "payload": "",
                            },
                            status=status.HTTP_200_OK,
                        )
                    except Exception:
                        logger.error(
                            "Error while sending email for password reset due to sendgrid",
                            exc_info=True,
                        )
                        # print("Error While sending email for password reset due to sendgrid : \n" + traceback.format_exc())
                        return Response(
                            {
                                "status": "error",
                                "message": "Error while sending email for password reset",
                                "payload": "",
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                else:
                    return Response(
                        data={
                            "status": "error",
                            "message": "User with this email not found",
                            "payload": {
                                "email": [
                                    "User with this email not found, Please Sign Up first on our platform"
                                ]
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            else:
                return Response(
                    data={
                        "status": "error",
                        "message": "Error in input data",
                        "payload": serialized.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception:
            logger.error(
                "Fatal error while sending email for password reset", exc_info=True
            )
            # print("Fatal Error While Logging In : \n" + traceback.format_exc())
            return Response(
                {
                    "status": "error",
                    "message": "Fatal error while sending email for password reset",
                    "payload": "",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetConfirmView(GenericAPIView):
    post_request_serializer_class = PasswordResetConfirmPostRequestSerializer
    token_generator = PasswordResetTokenGenerator()

    def get(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and self.token_generator.check_token(user, token):
            return Response({
                "status": "success",
                "message": "Valid link, you can proceed to change your password",
                "payload": ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Reset password link is invalid or expired!",
                "payload": "",
                "code": ErrorCode.LINK_EXPIRED
            }, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, uidb64, token):
        request_data = request.data
        serialized = self.post_request_serializer_class(data=request_data)
        serialized.is_valid(raise_exception=True)
        validated_data = serialized.validated_data
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(user_uid=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and self.token_generator.check_token(user, token):
            new_password = validated_data.get("new_password")
            user.set_password(new_password)
            user.save()
            return Response({
                "status": "success",
                "message": "Successfully changed password, you can now login with new password",
                "payload": ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Reset password link is invalid or expired!",
                "payload": "",
                "code": ErrorCode.LINK_EXPIRED
            }, status=status.HTTP_403_FORBIDDEN)