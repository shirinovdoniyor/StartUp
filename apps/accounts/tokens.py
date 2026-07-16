"""Short-lived signed tokens for the auth flow.

These are NOT JWT access tokens. They are stateless, signed, single-purpose
tokens (via django.core.signing) exchanged between OTP verification and the
registration / password-reset steps.
"""

from apps.common.exceptions import ApplicationError
from django.conf import settings
from django.core import signing

_REGISTRATION_SALT = "accounts.registration"
_RESET_SALT = "accounts.reset-password"


def issue_registration_token(phone: str) -> str:
    return signing.dumps({"phone": phone, "scope": "register"}, salt=_REGISTRATION_SALT)


def verify_registration_token(token: str) -> str:
    try:
        data = signing.loads(
            token, salt=_REGISTRATION_SALT, max_age=settings.REGISTRATION_TOKEN_TTL_SECONDS
        )
    except signing.SignatureExpired:
        raise ApplicationError("Ro'yxatdan o'tish tokeni muddati tugagan.")
    except signing.BadSignature:
        raise ApplicationError("Ro'yxatdan o'tish tokeni yaroqsiz.")
    if data.get("scope") != "register":
        raise ApplicationError("Token noto'g'ri maqsad uchun.")
    return data["phone"]


def issue_reset_token(phone: str) -> str:
    return signing.dumps({"phone": phone, "scope": "reset"}, salt=_RESET_SALT)


def verify_reset_token(token: str) -> str:
    try:
        data = signing.loads(token, salt=_RESET_SALT, max_age=settings.RESET_TOKEN_TTL_SECONDS)
    except signing.SignatureExpired:
        raise ApplicationError("Parolni tiklash tokeni muddati tugagan.")
    except signing.BadSignature:
        raise ApplicationError("Parolni tiklash tokeni yaroqsiz.")
    if data.get("scope") != "reset":
        raise ApplicationError("Token noto'g'ri maqsad uchun.")
    return data["phone"]
