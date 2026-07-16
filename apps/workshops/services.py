"""Write-side business logic for workshops and locations."""

from apps.common.exceptions import ApplicationError, PermissionError
from django.db import transaction
from django.utils.text import slugify
from django.utils.crypto import get_random_string

from .enums import WorkshopStatus
from .geocoding import get_coordinates
from .models import (
    Favorite,
    LocationImage,
    LocationService,
    Workshop,
    WorkshopLocation,
    WorkingHour,
)


def _unique_slug(model, base: str, *, scope: dict | None = None) -> str:
    base_slug = slugify(base) or get_random_string(8).lower()
    slug = base_slug
    qs = model.objects.all()
    if scope:
        qs = qs.filter(**scope)
    while qs.filter(slug=slug).exists():
        slug = f"{base_slug}-{get_random_string(4).lower()}"
    return slug


def ensure_owner(workshop: Workshop, user) -> None:
    from apps.accounts.enums import UserRole

    if user.role == UserRole.SUPER_ADMIN:
        return
    if workshop.owner_id != user.id:
        raise PermissionError("Bu workshop sizga tegishli emas.")


# --- Workshop ----------------------------------------------------------------
@transaction.atomic
def create_workshop(*, owner, data: dict) -> Workshop:
    data = dict(data)
    data.setdefault("slug", _unique_slug(Workshop, data.get("name", "")))
    return Workshop.objects.create(owner=owner, **data)


@transaction.atomic
def update_workshop(*, workshop: Workshop, data: dict) -> Workshop:
    for field, value in data.items():
        setattr(workshop, field, value)
    workshop.save()
    return workshop


def delete_workshop(*, workshop: Workshop) -> None:
    workshop.soft_delete()


# --- Location ----------------------------------------------------------------
@transaction.atomic
def create_location(*, workshop: Workshop, data: dict) -> WorkshopLocation:
    data = dict(data)
    if data.get("latitude") is None or data.get("longitude") is None:
        lat, lng = get_coordinates(data.get("address", ""))
        if lat is None:
            raise ApplicationError("Manzil koordinatalarini aniqlab bo'lmadi. latitude/longitude yuboring.")
        data["latitude"], data["longitude"] = lat, lng
    data.setdefault("slug", _unique_slug(WorkshopLocation, data.get("name", ""), scope={"workshop": workshop}))

    if data.get("is_main"):
        WorkshopLocation.objects.filter(workshop=workshop, is_main=True).update(is_main=False)

    return WorkshopLocation.objects.create(workshop=workshop, **data)


@transaction.atomic
def update_location(*, location: WorkshopLocation, data: dict) -> WorkshopLocation:
    data = dict(data)
    if "address" in data and ("latitude" not in data or "longitude" not in data):
        lat, lng = get_coordinates(data["address"])
        if lat is not None:
            data["latitude"], data["longitude"] = lat, lng
    if data.get("is_main"):
        WorkshopLocation.objects.filter(workshop=location.workshop, is_main=True).exclude(id=location.id).update(
            is_main=False
        )
    for field, value in data.items():
        setattr(location, field, value)
    location.save()
    return location


def delete_location(*, location: WorkshopLocation) -> None:
    location.delete()


# --- Location services (offerings) -------------------------------------------
@transaction.atomic
def add_location_service(*, location: WorkshopLocation, data: dict) -> LocationService:
    if LocationService.objects.filter(location=location, service=data["service"]).exists():
        raise ApplicationError("Bu xizmat ushbu filialga oldin qo'shilgan.")
    return LocationService.objects.create(location=location, **data)


@transaction.atomic
def update_location_service(*, offering: LocationService, data: dict) -> LocationService:
    for field, value in data.items():
        setattr(offering, field, value)
    offering.save()
    return offering


# --- Working hours / images --------------------------------------------------
@transaction.atomic
def set_working_hours(*, location: WorkshopLocation, hours: list[dict]) -> list[WorkingHour]:
    location.working_hours.all().delete()
    return WorkingHour.objects.bulk_create(
        [WorkingHour(location=location, **h) for h in hours]
    )


@transaction.atomic
def add_location_image(*, location: WorkshopLocation, data: dict) -> LocationImage:
    if data.get("is_primary"):
        LocationImage.objects.filter(location=location, is_primary=True).update(is_primary=False)
    return LocationImage.objects.create(location=location, **data)


# --- Favorites ---------------------------------------------------------------
def add_favorite(*, user, location: WorkshopLocation) -> Favorite:
    favorite, _ = Favorite.objects.get_or_create(user=user, location=location)
    return favorite


def remove_favorite(*, user, location_id) -> bool:
    deleted, _ = Favorite.objects.filter(user=user, location_id=location_id).delete()
    return bool(deleted)
