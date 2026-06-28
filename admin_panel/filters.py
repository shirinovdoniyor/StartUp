import django_filters

from users.models import User


class AdminUserFilter(django_filters.FilterSet):

    class Meta:
        model = User
        fields = {
            "is_active": ["exact"],
            "is_staff": ["exact"],
        }