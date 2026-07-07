import random
import re
import logging
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import  inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .serializer import UserProfileSerializer, NotificationSerializer
from .models import OTP, Notification

logger = logging.getLogger(__name__)
User = get_user_model()

MAX_OTP_ATTEMPTS = 5  # Brute-force himoya


def generate_otp_code() -> str:
    return str(random.randint(100000, 999999))


def is_valid_phone(phone: str) -> bool:
    """O'zbek raqam formatini tekshiradi: +998XXXXXXXXX"""
    return bool(re.match(r"^\+998\d{9}$", phone))


def get_tokens_for_user(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


#  SEND OTP
# ──────────────────────────────────────────────────────────
@extend_schema(
    tags=["Authentication"],
    summary="OTP yuborish",
    request=inline_serializer(
        name="SendOTPRequest",
        fields={"phone": serializers.CharField(help_text="+998901234567")},
    ),
    responses={
        200: inline_serializer(
            name="SendOTPResponse",
            fields={"message": serializers.CharField()},
        )
    },
)
@api_view(["POST"])
def send_otp(request):
    phone = request.data.get("phone", "").strip()

    if not phone:
        return Response({"error": "Telefon raqam majburiy"}, status=400)

    if not is_valid_phone(phone):
        return Response(
            {"error": "Noto'g'ri format. Masalan: +998901234567"}, status=400
        )

    # Eski OTPlarni o'chirish
    OTP.objects.filter(phone=phone).delete()

    # code = generate_otp_code()
    code='1234'
    OTP.objects.create(phone=phone, code=code)

    # message = f"Sizning tasdiqlash kodingiz: {code}\nUni hech kimga bermang."
    #
    # try:
    #     send_sms(phone, message)
    # except Exception as e:
    #     logger.error("OTP SMS xatosi [%s]: %s", phone, e)
    #     return Response({"error": "SMS yuborilmadi. Keyinroq urinib ko'ring."}, status=503)

    return Response({"message": "OTP yuborildi"})


#  VERIFY OTP
# ──────────────────────────────────────────────────────────
@extend_schema(
    tags=["Authentication"],
    summary="OTP tasdiqlash va login",
    request=inline_serializer(
        name="VerifyOTPRequest",
        fields={
            "phone": serializers.CharField(),
            "code": serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="VerifyOTPResponse",
            fields={
                "message": serializers.CharField(),
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
                "is_new_user": serializers.BooleanField(),
            },
        )
    },
)
@api_view(["POST"])
def verify_otp(request):
    phone = request.data.get("phone", "").strip()
    code = request.data.get("code", "").strip()

    if not phone or not code:
        return Response({"error": "Telefon va kod majburiy"}, status=400)

    try:
        otp = OTP.objects.filter(phone=phone).latest("created_at")
    except OTP.DoesNotExist:
        return Response({"error": "OTP topilmadi. Qayta yuborish kerak."}, status=400)

    # Brute-force himoya
    if otp.attempts >= MAX_OTP_ATTEMPTS:
        OTP.objects.filter(phone=phone).delete()
        return Response(
            {"error": "Urinishlar soni oshib ketdi. Yangi OTP so'rang."}, status=429
        )

    # Vaqt tekshiruvi
    if otp.is_expired():
        OTP.objects.filter(phone=phone).delete()
        return Response({"error": "OTP muddati tugagan. Qayta yuborish kerak."}, status=400)

    # Kod tekshiruvi
    if otp.code != code:
        otp.attempts += 1
        otp.save(update_fields=["attempts"])
        remaining = MAX_OTP_ATTEMPTS - otp.attempts
        return Response(
            {"error": f"Noto'g'ri kod. {remaining} ta urinish qoldi."}, status=400
        )

    # OTPni o'chirish
    OTP.objects.filter(phone=phone).delete()

    # Foydalanuvchini yaratish yoki olish
    user, is_new_user = User.objects.get_or_create(
        phone=phone,
        defaults={
            "name": ""
        }
    )
    print(user)
    print(is_new_user)
    tokens = get_tokens_for_user(user)

    return Response(
        {
            "message": "Muvaffaqiyatli kirildi",
            "is_new_user": is_new_user,
            **tokens,
        }
    )


@extend_schema(
    tags=["Authentication"],
    summary="Logout",
    request=inline_serializer(
        name="LogoutRequest",
        fields={
            "refresh": serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="LogoutResponse",
            fields={"message": serializers.CharField()},
        )
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response({"error": "Refresh token required"}, status=400)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response({"error": "Invalid or expired refresh token"}, status=400)

    return Response({"message": "Logout successful"}, status=200)

# ----------------GET-------------



@extend_schema(
    tags=["Authentication"],

    responses=UserProfileSerializer,
    description="Get current user profile"
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)




# ----------------PATCH----------------

@extend_schema(
    tags=["Authentication"],

    request=UserProfileSerializer,
    responses=UserProfileSerializer,
    description="Update current user profile"
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):

    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@extend_schema(
    tags=["Notifications"],
    summary="Get my notifications",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    notifications = request.user.notifications.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=["Notifications"],
    summary="Mark notification as read",
    request=None,
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def read_notification(request, notification_id):
    try:
        notification = request.user.notifications.get(id=notification_id)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=404)

    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])
    return Response(NotificationSerializer(notification).data)


@extend_schema(
    tags=["Notifications"],
    summary="Delete notification",
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    try:
        notification = request.user.notifications.get(id=notification_id)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=404)

    notification.delete()
    return Response(status=204)