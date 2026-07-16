"""Phone number normalisation and validation (Uzbekistan: +998XXXXXXXXX)."""

import re

PHONE_RE = re.compile(r"^\+998\d{9}$")


def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("998") and not phone.startswith("+"):
        phone = "+" + phone
    return phone


def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone))
