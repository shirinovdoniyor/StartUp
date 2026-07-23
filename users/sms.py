from django.conf import settings
from eskiz import EskizSMS


def send_sms(phone: str, message: str):
    with EskizSMS(
        email=settings.ESKIZ_EMAIL,
        password=settings.ESKIZ_PASSWORD,
    ) as client:

        response = client.sms.send(
            mobile_phone=phone,
            message=message,
            from_whom=settings.ESKIZ_SENDER,
        )

        return response

