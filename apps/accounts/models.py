import uuid

from apps.common.models import UUIDModel
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

from .enums import OtpPurpose, UserRole, UserStatus
from .managers import UserManager


class User(AbstractBaseUser):
    """Custom user keyed by phone.

    The `password` attribute is mapped to the `password_hash` column so the
    physical schema matches the target DDL while Django auth keeps working.
    Staff/superuser semantics are derived from `role`.
    """

    last_login = None  # not part of the target schema

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    password = models.TextField(db_column="password_hash")
    role = models.CharField(max_length=14, choices=UserRole.choices, default=UserRole.CUSTOMER)
    status = models.CharField(max_length=7, choices=UserStatus.choices, default=UserStatus.ACTIVE)
    avatar_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        constraints = [
            models.CheckConstraint(condition=models.Q(role__in=UserRole.values), name="users_valid_role"),
            models.CheckConstraint(condition=models.Q(status__in=UserStatus.values), name="users_valid_status"),
        ]

    def __str__(self):
        return self.phone

    # --- Derived profile helpers -------------------------------------------------
    @property
    def full_name(self):
        return " ".join(part for part in (self.first_name, self.last_name) if part)

    # --- Auth/permission semantics derived from role ----------------------------
    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE and self.deleted_at is None

    @property
    def is_staff(self):
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_superuser(self):
        return self.role == UserRole.SUPER_ADMIN

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = UserStatus.BLOCKED
        self.save(update_fields=["deleted_at", "status", "updated_at"])


class OTP(UUIDModel):
    """One-time password.

    The code is stored hashed (never in plaintext). Each OTP is scoped to a
    purpose, expires after an absolute `expires_at`, and is single-use
    (`consumed_at`).
    """

    phone = models.CharField(max_length=20)
    code_hash = models.CharField(max_length=255)
    purpose = models.CharField(max_length=14, choices=OtpPurpose.choices, default=OtpPurpose.LOGIN)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_otps"
        verbose_name = "OTP"
        indexes = [models.Index(fields=["phone", "purpose"], name="user_otps_phone_purpose_idx")]

    def set_code(self, raw_code: str) -> None:
        self.code_hash = make_password(raw_code)

    def check_code(self, raw_code: str) -> bool:
        return check_password(raw_code, self.code_hash)

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    def consume(self) -> None:
        self.consumed_at = timezone.now()
        self.save(update_fields=["consumed_at"])

    def __str__(self):
        return f"{self.phone} ({self.purpose})"
