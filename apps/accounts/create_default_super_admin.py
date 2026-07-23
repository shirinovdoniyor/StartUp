# apps/accounts/management/commands/create_default_super_admin.py

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.enums import UserRole, UserStatus


class Command(BaseCommand):
    help = "Create or refresh the default super admin for local testing"

    def handle(self, *args, **options):
        User = get_user_model()

        phone = "901234567"
        password = "Admin12345!"
        first_name = "Admin"
        last_name = "Test"
        email = "admin@test.local"

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "role": UserRole.SUPER_ADMIN,
                "status": UserStatus.ACTIVE,
                "deleted_at": None,
            },
        )

        changed = created

        if user.first_name != first_name:
            user.first_name = first_name
            changed = True

        if user.last_name != last_name:
            user.last_name = last_name
            changed = True

        if user.email != email:
            user.email = email
            changed = True

        if user.role != UserRole.SUPER_ADMIN:
            user.role = UserRole.SUPER_ADMIN
            changed = True

        if user.status != UserStatus.ACTIVE:
            user.status = UserStatus.ACTIVE
            changed = True

        if user.deleted_at is not None:
            user.deleted_at = None
            changed = True

        if not user.check_password(password):
            user.set_password(password)
            changed = True

        if changed:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Super admin ready: {phone}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Super admin already exists: {phone}"))
