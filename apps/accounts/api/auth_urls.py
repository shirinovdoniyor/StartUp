from django.urls import path

from . import auth_views, password_auth_views as pw

urlpatterns = [
    # --- Password-based auth (requirements 1-6) ---
    path("send-otp/", pw.send_otp, name="auth-register-send-otp"),
    path("verify-otp/", pw.verify_otp, name="auth-register-verify-otp"),
    path("register/", pw.register, name="auth-register"),
    path("login/", pw.login, name="auth-login"),
    path("forgot-password/", pw.forgot_password, name="auth-forgot-password"),
    path("verify-reset-otp/", pw.verify_reset_otp, name="auth-verify-reset-otp"),
    path("reset-password/", pw.reset_password, name="auth-reset-password"),
    # --- Legacy passwordless OTP login (kept) ---
    path("otp/send/", auth_views.send_otp, name="auth-send-otp"),
    path("otp/verify/", auth_views.verify_otp, name="auth-verify-otp"),
    path("logout/", auth_views.logout, name="auth-logout"),
    path("change-phone/send-otp/", auth_views.change_phone_send_otp, name="auth-change-phone-send"),
    path("change-phone/verify/", auth_views.change_phone_verify, name="auth-change-phone-verify"),
]
