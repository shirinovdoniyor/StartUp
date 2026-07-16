from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .. import services
from ..serializers import (
    AuthTokenSerializer,
    ChangePhoneConfirmSerializer,
    ChangePhoneRequestSerializer,
    LogoutSerializer,
    MessageSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
)


@extend_schema(tags=["Auth"], request=SendOTPSerializer, responses=MessageSerializer, summary="Send OTP")
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    services.request_otp(serializer.validated_data["phone"].strip())
    return Response({"message": "OTP muvaffaqiyatli yuborildi."})


@extend_schema(tags=["Auth"], request=VerifyOTPSerializer, responses=AuthTokenSerializer, summary="Verify OTP & login")
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = services.verify_otp_and_login(
        serializer.validated_data["phone"].strip(),
        serializer.validated_data["code"].strip(),
    )
    return Response(result, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"], request=LogoutSerializer, responses=MessageSerializer, summary="Logout")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    services.logout(request.data.get("refresh"))
    return Response({"message": "Successfully logged out."})


@extend_schema(tags=["Auth"], request=ChangePhoneRequestSerializer, responses=MessageSerializer, summary="Change phone - send OTP")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_phone_send_otp(request):
    serializer = ChangePhoneRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    services.change_phone_request(request.user, serializer.validated_data["new_phone"].strip())
    return Response({"message": "OTP yuborildi."})


@extend_schema(tags=["Auth"], request=ChangePhoneConfirmSerializer, responses=MessageSerializer, summary="Change phone - verify")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_phone_verify(request):
    serializer = ChangePhoneConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    services.change_phone_confirm(
        request.user,
        serializer.validated_data["new_phone"].strip(),
        serializer.validated_data["code"].strip(),
    )
    return Response({"message": "Telefon raqam muvaffaqiyatli yangilandi."})
