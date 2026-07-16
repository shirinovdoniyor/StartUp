"""Eskiz SMS integration."""

import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

ESKIZ_TOKEN_CACHE_KEY = "eskiz_token"
ESKIZ_TOKEN_TTL = 60 * 60 * 23  

def get_eskiz_token() -> str:
    token = cache.get(ESKIZ_TOKEN_CACHE_KEY)
    if token:
        return token

    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Eskiz login error: %s", exc)
        raise RuntimeError("Eskiz bilan ulanib bo'lmadi") from exc

    token = response.json().get("data", {}).get("token")
    if not token:
        raise RuntimeError("Eskiz tokenini olishda xato")

    cache.set(ESKIZ_TOKEN_CACHE_KEY, token, ESKIZ_TOKEN_TTL)
    return token


def send_sms(phone: str, message: str) -> dict:
    token = get_eskiz_token()
    url = "https://notify.eskiz.uz/api/message/sms/send"
    clean_phone = "".join(filter(str.isdigit, phone))
    payload = {"mobile_phone": clean_phone, "message": message, "from": settings.ESKIZ_SENDER}
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("SMS send error [%s]: %s", phone, exc)
        raise RuntimeError("SMS yuborishda xato yuz berdi") from exc
    return response.json()
