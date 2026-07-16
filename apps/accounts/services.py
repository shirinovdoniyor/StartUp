"""Application/service layer for accounts & authentication.

Business rules live here. Persistence goes through the repository layer;
transport concerns (HTTP) live in the API layer. (Clean Architecture)
"""

import secrets

from apps.common.exceptions import ApplicationError, NotFoundError
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from .enums import OtpPurpose, UserRole, UserStatus
from .models import User
from .phone import is_valid_phone, normalize_phone
from .repositories import otp_repository, user_repository
from .sms import send_sms
from .tokens import issue_registration_token, issue_reset_token


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
def issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------
def send_otp(*, phone: str, purpose: str) -> None:
    """Generate, persist (hashed) and deliver a one-time password."""
    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        raise ApplicationError("Telefon raqam formati noto'g'ri.")

    otp_repository.invalidate_all(phone=phone, purpose=purpose)
    code = _generate_code()
    otp_repository.create(
        phone=phone, raw_code=code, purpose=purpose, ttl_minutes=settings.OTP_TTL_MINUTES
    )

    message = f"Sizning tasdiqlash kodingiz: {code}"
    if settings.OTP_DEBUG_ECHO:
        print("=" * 40, f"\nOTP [{purpose}] {phone}: {code}\n", "=" * 40)
    else:
        send_sms(phone, message)


def verify_otp(*, phone: str, code: str, purpose: str):
    """Validate and consume an OTP. Returns the consumed OTP on success."""
    phone = normalize_phone(phone)
    otp = otp_repository.latest_active(phone=phone, purpose=purpose)
    if otp is None:
        raise NotFoundError("OTP topilmadi. Avval kod yuboring.")

    if otp.is_expired:
        raise ApplicationError("OTP muddati tugagan. Qayta kod yuboring.")

    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise ApplicationError("Juda ko'p noto'g'ri urinish. Yangi OTP yuboring.")

    if not otp.check_code(code):
        otp.attempts += 1
        otp_repository.save(otp, update_fields=["attempts"])
        remaining = settings.OTP_MAX_ATTEMPTS - otp.attempts
        raise ApplicationError(f"Noto'g'ri OTP. {remaining} ta urinish qoldi.")

    otp.consume()  # single-use
    return otp


# ---------------------------------------------------------------------------
# Registration flow (send-otp -> verify-otp -> register)
# ---------------------------------------------------------------------------
def start_registration_otp(*, phone: str) -> None:
    phone = normalize_phone(phone)
    if user_repository.exists_by_phone(phone):
        raise ApplicationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
    send_otp(phone=phone, purpose=OtpPurpose.REGISTER)


def verify_registration_otp(*, phone: str, code: str) -> str:
    """Verify OTP and return a short-lived signed registration token."""
    verify_otp(phone=normalize_phone(phone), code=code, purpose=OtpPurpose.REGISTER)
    return issue_registration_token(normalize_phone(phone))


def _validate_password(raw_password: str) -> None:
    try:
        validate_password(raw_password)
    except DjangoValidationError as exc:
        raise ApplicationError(list(exc.messages))


@transaction.atomic
def register(*, phone: str, first_name: str, last_name: str, password: str) -> dict:
    phone = normalize_phone(phone)
    if user_repository.exists_by_phone(phone):
        raise ApplicationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
    _validate_password(password)

    user = user_repository.create(
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        password=password,
        role=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE,
    )
    return {"user": user, **issue_tokens(user)}


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def login(*, phone: str, password: str) -> dict:
    phone = normalize_phone(phone)
    user = user_repository.get_by_phone(phone)
    if user is None or not user.check_password(password):
        raise ApplicationError("Telefon raqam yoki parol noto'g'ri.")
    if not user.is_active:
        raise ApplicationError("Hisob bloklangan yoki faol emas.")
    return {"user": user, **issue_tokens(user)}


# ---------------------------------------------------------------------------
# Forgot / reset password
# ---------------------------------------------------------------------------
def forgot_password(*, phone: str) -> None:
    phone = normalize_phone(phone)
    # Avoid user enumeration: only send if a user exists, but respond identically.
    if user_repository.exists_by_phone(phone):
        send_otp(phone=phone, purpose=OtpPurpose.RESET_PASSWORD)


def verify_reset_otp(*, phone: str, code: str) -> str:
    verify_otp(phone=normalize_phone(phone), code=code, purpose=OtpPurpose.RESET_PASSWORD)
    return issue_reset_token(normalize_phone(phone))


@transaction.atomic
def reset_password(*, phone: str, new_password: str) -> None:
    phone = normalize_phone(phone)
    user = user_repository.get_by_phone(phone)
    if user is None:
        raise NotFoundError("Foydalanuvchi topilmadi.")
    _validate_password(new_password)
    user_repository.set_password(user, new_password)


# ---------------------------------------------------------------------------
# Legacy passwordless OTP login (kept for existing /auth/otp/* endpoints)
# ---------------------------------------------------------------------------
@transaction.atomic
def verify_otp_and_login(phone: str, code: str) -> dict:
    phone = normalize_phone(phone)
    verify_otp(phone=phone, code=code, purpose=OtpPurpose.LOGIN)
    user = user_repository.get_by_phone(phone)
    is_new = False
    if user is None:
        user = user_repository.create(phone=phone, first_name="")
        is_new = True
    return {"is_new_user": is_new, **issue_tokens(user)}


def request_otp(phone: str) -> None:
    """Legacy alias: send a LOGIN-purpose OTP."""
    send_otp(phone=phone, purpose=OtpPurpose.LOGIN)


# ---------------------------------------------------------------------------
# Change phone (authenticated)
# ---------------------------------------------------------------------------
@transaction.atomic
def change_phone_request(user: User, new_phone: str) -> None:
    new_phone = normalize_phone(new_phone)
    if not is_valid_phone(new_phone):
        raise ApplicationError("Telefon raqam noto'g'ri.")
    if user_repository.get_by_phone(new_phone) and user_repository.get_by_phone(new_phone).id != user.id:
        raise ApplicationError("Bu telefon raqam allaqachon mavjud.")
    send_otp(phone=new_phone, purpose=OtpPurpose.LOGIN)


@transaction.atomic
def change_phone_confirm(user: User, new_phone: str, code: str) -> None:
    new_phone = normalize_phone(new_phone)
    if not new_phone or not code:
        raise ApplicationError("Barcha maydonlar majburiy.")
    verify_otp(phone=new_phone, code=code, purpose=OtpPurpose.LOGIN)
    user.phone = new_phone
    user.save(update_fields=["phone", "updated_at"])


def logout(refresh_token: str | None) -> None:
    if not refresh_token:
        return
    try:
        RefreshToken(refresh_token).blacklist()
    except Exception:
        pass


def update_profile(user: User, data: dict) -> User:
    editable = {"first_name", "last_name", "email", "avatar_url"}
    changed = []
    for field in editable:
        if field in data:
            setattr(user, field, data[field])
            changed.append(field)
    if changed:
        changed.append("updated_at")
        user.save(update_fields=changed)
    return user
