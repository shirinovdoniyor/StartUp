from django.contrib.auth.base_user import BaseUserManager

from .enums import UserRole, UserStatus


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Telefon raqam majburiy")
        extra_fields.setdefault("role", UserRole.CUSTOMER)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields["role"] = UserRole.SUPER_ADMIN
        extra_fields["status"] = UserStatus.ACTIVE
        if not password:
            raise ValueError("Superuser uchun parol majburiy")
        extra_fields.setdefault("first_name", "Admin")
        return self.create_user(phone, password, **extra_fields)

    def active(self):
        return self.get_queryset().filter(
            status=UserStatus.ACTIVE, deleted_at__isnull=True
        )
