import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

ESKIZ_TOKEN_CACHE_KEY = "eskiz_token"
ESKIZ_TOKEN_TTL = 60 * 60 * 23  # 23 soat (token 24 soat amal qiladi)


def get_eskiz_token() -> str:
    """
    Eskiz tokenini cache'dan oladi.
    Agar cache'da yo'q bo'lsa — yangi token so'raydi va saqlaydi.
    """
    token = cache.get(ESKIZ_TOKEN_CACHE_KEY)
    if token:
        return token

    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {
        "email": settings.ESKIZ_EMAIL,
        "password": settings.ESKIZ_PASSWORD,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Eskiz login xatosi: %s", e)
        raise Exception("Eskiz bilan ulanib bo'lmadi") from e

    data = response.json()
    token = data.get("data", {}).get("token")
    if not token:
        raise Exception("Eskiz tokenini olishda xato")

    cache.set(ESKIZ_TOKEN_CACHE_KEY, token, ESKIZ_TOKEN_TTL)
    return token


def send_sms(phone: str, message: str) -> dict:
    """
    Eskiz orqali SMS yuboradi.
    phone: +998901234567 yoki 998901234567 formatda
    """
    token = get_eskiz_token()
    url = "https://notify.eskiz.uz/api/message/sms/send"

    # Raqamni tozalash: faqat raqamlar qolsin
    clean_phone = "".join(filter(str.isdigit, phone))

    payload = {
        "mobile_phone": clean_phone,
        "message": message,
        "from": settings.ESKIZ_SENDER,  # masalan: "4546"
    }
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("SMS yuborish xatosi [%s]: %s", phone, e)
        raise Exception("SMS yuborishda xato yuz berdi") from e

    result = response.json()
    logger.info("SMS yuborildi [%s]: %s", phone, result.get("status"))
    return result