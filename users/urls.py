from django.urls import path
from .views import (
    send_otp,
    verify_otp,
    get_profile,
    update_profile,
    logout,
    list_notifications,
    read_notification,
    delete_notification,
)

urlpatterns = [
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("logout/", logout, name="logout"),
    path("profile/", get_profile, name="get-profile"),
    path("profile/update/", update_profile, name="update-profile"),
    path("notifications/", list_notifications, name="notifications-list"),
    path("notifications/<uuid:notification_id>/read/", read_notification, name="notification-read"),
    path("notifications/<uuid:notification_id>/delete/", delete_notification, name="notification-delete"),
]