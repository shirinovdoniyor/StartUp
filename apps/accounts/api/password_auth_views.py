"""Password-based authentication endpoints.

Flow:
    send-otp  -> verify-otp (returns registration_token) -> register
    login
    forgot-password -> reset-password
"""

from apps.accounts import services
from apps.accounts.serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    MessageSerializer,
    PhoneSerializer,
    RegisterSerializer,
    RegistrationTokenSerializer,
    ResetPasswordSerializer,
    ResetTokenSerializer,
    TokenPairWithUserSerializer,
    UserProfileSerializer,
    VerifyRegistrationOTPSerializer,
    VerifyResetOTPSerializer,
)
from apps.accounts.tokens import verify_registration_token, verify_reset_token
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(
    tags=["Auth"],
    request=PhoneSerializer,
    responses=MessageSerializer,
    summary="Send registration OTP",
    description="Sends a 6-digit OTP (valid 5 minutes, single-use) to the phone for registration.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = PhoneSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    services.start_registration_otp(phone=serializer.validated_data["phone"])
    return Response({"message": "OTP yuborildi."})


@extend_schema(
    tags=["Auth"],
    request=VerifyRegistrationOTPSerializer,
    responses=RegistrationTokenSerializer,
    summary="Verify registration OTP",
    description="Verifies the OTP and returns a short-lived signed registration token (not a JWT).",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyRegistrationOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = services.verify_registration_otp(
        phone=serializer.validated_data["phone"],
        code=serializer.validated_data["code"],
    )
    return Response({"registration_token": token})


@extend_schema(
    tags=["Auth"],
    request=RegisterSerializer,
    responses=TokenPairWithUserSerializer,
    summary="Register",
    description="Creates a user from the verified phone (registration token) with a bcrypt-hashed password.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    phone = verify_registration_token(data["registration_token"])
    result = services.register(
        phone=phone,
        first_name=data["first_name"],
        last_name=data.get("last_name", ""),
        password=data["password"],
    )
    payload = {
        "access": result["access"],
        "refresh": result["refresh"],
        "user": UserProfileSerializer(result["user"]).data,
    }
    return Response(payload, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Auth"],
    request=LoginSerializer,
    responses=TokenPairWithUserSerializer,
    summary="Login",
    description="Authenticates with phone + password and returns access & refresh tokens.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = services.login(
        phone=serializer.validated_data["phone"],
        password=serializer.validated_data["password"],
    )
    payload = {
        "access": result["access"],
        "refresh": result["refresh"],
        "user": UserProfileSerializer(result["user"]).data,
    }
    return Response(payload, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    request=ForgotPasswordSerializer,
    responses=MessageSerializer,
    summary="Forgot password",
    description="Sends a password-reset OTP if an account exists for the phone.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    services.forgot_password(phone=serializer.validated_data["phone"])
    return Response({"message": "Agar hisob mavjud bo'lsa, OTP yuborildi."})


@extend_schema(
    tags=["Auth"],
    request=VerifyResetOTPSerializer,
    responses=ResetTokenSerializer,
    summary="Verify reset OTP",
    description="Verifies the password-reset OTP and returns a short-lived signed reset token.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_reset_otp(request):
    serializer = VerifyResetOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = services.verify_reset_otp(
        phone=serializer.validated_data["phone"],
        code=serializer.validated_data["code"],
    )
    return Response({"reset_token": token})


@extend_schema(
    tags=["Auth"],
    request=ResetPasswordSerializer,
    responses=MessageSerializer,
    summary="Reset password",
    description="Verifies the reset token and updates the password (bcrypt-hashed).",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = verify_reset_token(serializer.validated_data["reset_token"])
    services.reset_password(phone=phone, new_password=serializer.validated_data["new_password"])
    return Response({"message": "Parol muvaffaqiyatli yangilandi."})
