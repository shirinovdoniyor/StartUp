from django.contrib import admin

from .models import OTP, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "first_name", "last_name", "role", "status", "created_at")
    list_filter = ("role", "status")
    search_fields = ("phone", "first_name", "last_name", "email")


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone", "purpose", "attempts", "expires_at", "consumed_at", "created_at")
    list_filter = ("purpose",)
    search_fields = ("phone",)
    readonly_fields = ("code_hash",)
