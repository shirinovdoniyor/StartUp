"""Read-side queries for accounts."""

from django.db.models import Q, QuerySet

from .models import User


def get_user_by_id(user_id) -> User:
    return User.objects.get(id=user_id)


def user_exists_by_phone(phone: str) -> bool:
    return User.objects.filter(phone=phone).exists()


def list_users(*, search: str = "", role: str = "", status: str = "") -> QuerySet[User]:
    qs = User.objects.all().order_by("-created_at")
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )
    if role:
        qs = qs.filter(role=role)
    if status:
        qs = qs.filter(status=status)
    return qs
