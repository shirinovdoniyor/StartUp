from django.urls import path
from .views import (
    send_otp, verify_otp, get_profile, update_profile, 
    change_phone_send_otp, change_phone_verify, logout,
    get_notifications, mark_notification_read, delete_notification
)

urlpatterns = [
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("logout/", logout, name="logout"),
    path("profile/", get_profile, name="get-profile"),
    path("profile/update/", update_profile, name="update-profile"),
    path("change-phone/send-otp/", change_phone_send_otp),
    path("change-phone/verify/", change_phone_verify),
    
    # Notifications
    path("notifications/", get_notifications, name="get-notifications"),
    path("notifications/<uuid:notification_id>/read/", mark_notification_read, name="mark-read"),
    path("notifications/<uuid:notification_id>/delete/", delete_notification, name="delete-notification"),
]