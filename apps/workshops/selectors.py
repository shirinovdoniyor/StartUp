from django.db.models import Prefetch, Q, QuerySet

from .enums import LocationStatus, WorkshopStatus
from .models import LocationService, Workshop, WorkshopLocation


def active_workshops() -> QuerySet[Workshop]:
    return Workshop.objects.filter(deleted_at__isnull=True)


def public_workshops(*, search: str = "") -> QuerySet[Workshop]:
    qs = active_workshops().filter(status=WorkshopStatus.APPROVED)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    return qs.prefetch_related("locations")


def workshops_for_owner(owner) -> QuerySet[Workshop]:
    return active_workshops().filter(owner=owner)


def get_workshop(workshop_id) -> Workshop:
    return active_workshops().get(id=workshop_id)


def locations_for_workshop(workshop_id) -> QuerySet[WorkshopLocation]:
    return WorkshopLocation.objects.filter(workshop_id=workshop_id).prefetch_related(
        "working_hours", "images"
    )


def active_locations() -> QuerySet[WorkshopLocation]:
    return WorkshopLocation.objects.filter(
        status=LocationStatus.ACTIVE, workshop__deleted_at__isnull=True
    )


def location_services_for_location(location_id) -> QuerySet[LocationService]:
    return (
        LocationService.objects.filter(location_id=location_id)
        .select_related("service", "service__category")
    )
