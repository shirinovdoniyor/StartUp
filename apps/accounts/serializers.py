from rest_framework import serializers

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "email",
            "role",
            "status",
            "avatar_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "phone", "role", "status", "created_at", "updated_at"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar_url"]
        extra_kwargs = {f: {"required": False} for f in fields}


# --- Auth request/response DTOs -------------------------------------------------
class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(help_text="+998901234567")


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()


class AuthTokenSerializer(serializers.Serializer):
    is_new_user = serializers.BooleanField()
    access = serializers.CharField()
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True)


class ChangePhoneRequestSerializer(serializers.Serializer):
    new_phone = serializers.CharField()


class ChangePhoneConfirmSerializer(serializers.Serializer):
    new_phone = serializers.CharField()
    code = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


# --- Password-based auth flow ---------------------------------------------------
class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(help_text="+998901234567")


class VerifyRegistrationOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)


class RegistrationTokenSerializer(serializers.Serializer):
    registration_token = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    registration_token = serializers.CharField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()


class VerifyResetOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)


class ResetTokenSerializer(serializers.Serializer):
    reset_token = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})


class TokenPairWithUserSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
