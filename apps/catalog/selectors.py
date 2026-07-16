from django.db.models import Q, QuerySet

from .models import Category, Service


def list_categories() -> QuerySet[Category]:
    return Category.objects.all()


def list_services(*, category_id=None, search: str = "") -> QuerySet[Service]:
    qs = Service.objects.select_related("category").prefetch_related("aliases")
    if category_id:
        qs = qs.filter(category_id=category_id)
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(aliases__alias__icontains=search)
        ).distinct()
    return qs
