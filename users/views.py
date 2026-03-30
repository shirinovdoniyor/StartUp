from django.shortcuts import render

import random
from datetime import timedelta
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import OTP
from .utils import send_sms
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

# -------------------------------send_otp --------------------------------
@extend_schema(
    request=inline_serializer(
        name='SendOTP',
        fields={
            'phone': serializers.CharField()
        }
    ),
    responses={200: inline_serializer(
        name='SendOTPResponse',
        fields={
            'message': serializers.CharField()
        }
    )}
)
@api_view(['POST'])
def send_otp(request):
    phone = request.data.get('phone')

    if not phone:
        return Response({"error": "Phone required"}, status=400)

    # eski OTPlarni o‘chiramiz
    OTP.objects.filter(phone=phone).delete()

    code = str(random.randint(100000, 999999))

    OTP.objects.create(phone=phone, code=code)

    message = f"Sizning tasdiqlash kodingiz: {code}"

    try:
        send_sms(phone, message)
    except Exception as e:
        return Response({"error": "SMS yuborilmadi", "detail": str(e)}, status=500)

    return Response({"message": "OTP sent"})


from django.contrib.auth import get_user_model
User = get_user_model()

# ---------------------------------verify_otp--------------

@extend_schema(
    request=inline_serializer(
        name='VerifyOTP',
        fields={
            'phone': serializers.CharField(),
            'code': serializers.CharField()
        }
    ),
    responses={200: inline_serializer(
        name='VerifyOTPResponse',
        fields={
            'message': serializers.CharField(),
            'user_id': serializers.IntegerField()
        }
    )}
)
@api_view(['POST'])
def verify_otp(request):
    phone = request.data.get('phone')
    code = request.data.get('code')

    try:
        otp = OTP.objects.filter(phone=phone, code=code).latest('created_at')
    except OTP.DoesNotExist:
        return Response({"error": "Invalid OTP"}, status=400)

    # ⏰ 2 minut limit
    if otp.created_at < timezone.now() - timedelta(minutes=2):
        return Response({"error": "OTP expired"}, status=400)

    user, created = User.objects.get_or_create(phone=phone)

    # OTPni o‘chiramiz
    OTP.objects.filter(phone=phone).delete()

    return Response({
        "message": "Logged in",
        "user_id": user.id
    })