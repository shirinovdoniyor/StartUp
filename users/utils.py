import requests
from django.conf import settings


def get_eskiz_token():
    url = "https://notify.eskiz.uz/api/auth/login"

    payload = {
        "email": settings.ESKIZ_EMAIL,
        "password": settings.ESKIZ_PASSWORD
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        raise Exception("Eskiz login error")

    return response.json()['data']['token']


def send_sms(phone, message):
    token = get_eskiz_token()

    url = "https://notify.eskiz.uz/api/message/sms/send"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "mobile_phone": phone.replace("+", ""),
        "message": message,
        "from": "4546"  # Eskiz beradi
    }

    response = requests.post(url, headers=headers, data=payload)

    return response.json()