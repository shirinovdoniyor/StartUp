"""Repository layer for the accounts domain.

Encapsulates all persistence access for User and OTP so the service layer
depends on an abstraction rather than the ORM directly (Repository Pattern).
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from .enums import OtpPurpose
from .models import OTP, User


class UserRepository:
    def get_by_id(self, user_id):
        return User.objects.filter(id=user_id).first()

    def get_by_phone(self, phone: str) -> User | None:
        return User.objects.filter(phone=phone).first()

    def exists_by_phone(self, phone: str) -> bool:
        return User.objects.filter(phone=phone).exists()

    def create(self, *, phone: str, first_name: str, last_name: str = "", password: str | None = None, **extra) -> User:
        return User.objects.create_user(
            phone=phone, first_name=first_name, last_name=last_name or "", password=password, **extra
        )

    def set_password(self, user: User, raw_password: str) -> User:
        user.set_password(raw_password)
        user.save(update_fields=["password", "updated_at"])
        return user


class OTPRepository:
    def create(self, *, phone: str, raw_code: str, purpose: str, ttl_minutes: int) -> OTP:
        otp = OTP(
            phone=phone,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
        )
        otp.set_code(raw_code)
        otp.save()
        return otp

    def latest_active(self, *, phone: str, purpose: str) -> OTP | None:
        return (
            OTP.objects.filter(phone=phone, purpose=purpose, consumed_at__isnull=True)
            .order_by("-created_at")
            .first()
        )

    def invalidate_all(self, *, phone: str, purpose: str) -> None:
        OTP.objects.filter(phone=phone, purpose=purpose, consumed_at__isnull=True).delete()

    def save(self, otp: OTP, *, update_fields=None) -> None:
        otp.save(update_fields=update_fields)


user_repository = UserRepository()
otp_repository = OTPRepository()
