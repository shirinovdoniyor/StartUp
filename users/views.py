import random
import re
import logging
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import  inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .serializer import UserProfileSerializer
from .models import OTP
from .utils import send_sms
logger = logging.getLogger(__name__)
User = get_user_model()


MAX_OTP_ATTEMPTS = 5  


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

# #  ------------------SEND OTP----------------------

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
        return Response(
            {"error": "Telefon raqam majburiy"},
            status=400
        )

    if not is_valid_phone(phone):
        return Response(
            {"error": "Telefon raqam formati noto'g'ri"},
            status=400
        )

    OTP.objects.filter(phone=phone).delete()

    # code = generate_otp_code()
    code="1234"
    OTP.objects.create(
        phone=phone,
        code=code,
    )

    print("=" * 50)
    print(f"OTP CODE -> {phone}: {code}")
    print("=" * 50)

    # Eskiz bilan shartnoma qilgandan so'ng
    # quyidagi kodni uncomment qilamiz va printni o'chiramiz

    """
    message = f"Sizning tasdiqlash kodingiz: {code}"

    try:
        send_sms(phone, message)
    except Exception as e:
        OTP.objects.filter(phone=phone).delete()
        return Response({"error": str(e)}, status=500)
    """

    return Response({
        "message": "OTP muvaffaqiyatli yuborildi."
    })
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
                "is_new_user": serializers.BooleanField(),
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
            },
        )
    },
)
@api_view(["POST"])
def verify_otp(request):

    phone = request.data.get("phone", "").strip()
    code = request.data.get("code", "").strip()

    if not phone:
        return Response(
            {"error": "Telefon raqam majburiy."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not code:
        return Response(
            {"error": "OTP kod majburiy."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not is_valid_phone(phone):
        return Response(
            {"error": "Telefon raqam formati noto'g'ri."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        otp = OTP.objects.filter(phone=phone).latest("created_at")

    except OTP.DoesNotExist:
        return Response(
            {"error": "OTP topilmadi. Avval kod yuboring."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # OTP muddati tugaganmi
    if otp.is_expired():
        otp.delete()

        return Response(
            {"error": "OTP muddati tugagan. Qayta kod yuboring."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Brute-force himoya
    if otp.attempts >= MAX_OTP_ATTEMPTS:
        otp.delete()

        return Response(
            {
                "error": "Juda ko'p noto'g'ri urinish. Yangi OTP yuboring."
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Kod tekshirish
    if otp.code != code:

        otp.attempts += 1
        otp.save(update_fields=["attempts"])

        remaining = MAX_OTP_ATTEMPTS - otp.attempts

        return Response(
            {
                "error": f"Noto'g'ri OTP. {remaining} ta urinish qoldi."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # OTP to'g'ri
    otp.delete()

    user, is_new_user = User.objects.get_or_create(
        phone=phone,
        defaults={
            "name": "",
        },
    )

    tokens = get_tokens_for_user(user)

    return Response(
        {
            "message": "Muvaffaqiyatli kirildi.",
            "is_new_user": is_new_user,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        },
        status=status.HTTP_200_OK,
    )
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



# ---------------------_# POST /change-phone/send-otp/--------------------
# POST /change-phone/send-otp/


@extend_schema(
    tags=["Authentication"],
    summary="Change phone - Send OTP",
    request=inline_serializer(
        name="ChangePhoneRequest",
        fields={
            "new_phone": serializers.CharField()
        }
    ),
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_phone_send_otp(request):

    new_phone = request.data.get("new_phone", "").strip()

    if not new_phone:
        return Response(
            {"error": "Yangi telefon raqam majburiy"},
            status=400
        )

    if not is_valid_phone(new_phone):
        return Response(
            {"error": "Telefon raqam noto'g'ri"},
            status=400
        )

    if User.objects.filter(phone=new_phone).exists():
        return Response(
            {"error": "Bu telefon raqam allaqachon mavjud"},
            status=400
        )

    OTP.objects.filter(phone=new_phone).delete()

    code = generate_otp_code()

    OTP.objects.create(
        phone=new_phone,
        code=code
    )

    message = f"Sizning tasdiqlash kodingiz: {code}"

    send_sms(new_phone, message)

    return Response({
        "message": "OTP yuborildi"
    })



# --------------POST /change-phone/verify/-----------------

@extend_schema(
    tags=["Authentication"],
    summary="Change phone - Verify OTP",
    request=inline_serializer(
        name="VerifyPhoneOTPRequest",
        fields={
            "new_phone": serializers.CharField(),
            "code": serializers.CharField(),
        }
    ),
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_phone_verify(request):

    new_phone = request.data.get("new_phone", "").strip()
    code = request.data.get("code", "").strip()

    if not new_phone or not code:
        return Response(
            {"error": "Barcha maydonlar majburiy"},
            status=400
        )

    try:
        otp = OTP.objects.filter(
            phone=new_phone
        ).latest("created_at")

    except OTP.DoesNotExist:
        return Response(
            {"error": "OTP topilmadi"},
            status=400
        )

    if otp.is_expired():
        otp.delete()

        return Response(
            {"error": "OTP muddati tugagan"},
            status=400
        )

    if otp.code != code:

        otp.attempts += 1
        otp.save()

        return Response(
            {"error": "Kod noto'g'ri"},
            status=400
        )

    request.user.phone = new_phone
    request.user.save(update_fields=["phone"])

    otp.delete()

    return Response({
        "message": "Telefon raqam muvaffaqiyatli yangilandi."
    })