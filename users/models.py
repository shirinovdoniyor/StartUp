import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, phone, **extra_fields):
        if not phone:
            raise ValueError("Telefon raqam majburiy")
        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveSmallIntegerField(default=0)  # brute-force himoya

    class Meta:
        indexes = [models.Index(fields=["phone"])]
        verbose_name = "OTP"

    def is_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(minutes=2)

    def __str__(self):
        return f"{self.phone} - {self.code}"