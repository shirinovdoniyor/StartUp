from django.db import models


class UserRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super admin"
    WORKSHOP_OWNER = "WORKSHOP_OWNER", "Workshop owner"
    CUSTOMER = "CUSTOMER", "Customer"


class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    BLOCKED = "BLOCKED", "Blocked"
    PENDING = "PENDING", "Pending"


class OtpPurpose(models.TextChoices):
    LOGIN = "LOGIN", "Login"
    REGISTER = "REGISTER", "Registration"
    RESET_PASSWORD = "RESET_PASSWORD", "Reset password"
