from django.urls import path
from .views import send_otp, verify_otp, get_profile, update_profile

urlpatterns = [
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("profile/", get_profile, name="get-profile"),
    path("profile/update/", update_profile, name="update-profile"),
]