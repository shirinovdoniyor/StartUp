from decimal import Decimal

from apps.common.models import UUIDModel, UUIDTimeStampedModel
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from .enums import LocationStatus, PriceType, WorkshopStatus


class Workshop(UUIDTimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workshops",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    logo_url = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    telegram = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=WorkshopStatus.choices, default=WorkshopStatus.PENDING)
    is_verified = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "workshops"
        ordering = ["-premium", "-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(status__in=WorkshopStatus.values), name="workshops_valid_status"),
        ]
        indexes = [models.Index(fields=["owner"], name="workshops_owner_idx")]

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = WorkshopStatus.BLOCKED
        self.save(update_fields=["deleted_at", "status", "updated_at"])


class WorkshopLocation(UUIDTimeStampedModel):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField()
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    is_main = models.BooleanField(default=False)
    status = models.CharField(max_length=8, choices=LocationStatus.choices, default=LocationStatus.ACTIVE)

    class Meta:
        db_table = "workshop_locations"
        indexes = [models.Index(fields=["workshop"], name="locations_workshop_idx")]
        constraints = [
            models.UniqueConstraint(fields=["workshop", "slug"], name="locations_workshop_slug_uniq"),
            models.UniqueConstraint(
                fields=["workshop"], condition=Q(is_main=True), name="locations_one_main_per_workshop"
            ),
            models.CheckConstraint(condition=Q(rating__gte=0, rating__lte=5), name="locations_rating_0_5"),
            models.CheckConstraint(condition=Q(status__in=LocationStatus.values), name="locations_valid_status"),
        ]

    def __str__(self):
        return f"{self.workshop.name} - {self.name}"


class WorkingHour(UUIDModel):
    location = models.ForeignKey(WorkshopLocation, on_delete=models.CASCADE, related_name="working_hours")
    day_of_week = models.PositiveSmallIntegerField()
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        db_table = "working_hours"
        ordering = ["day_of_week"]
        constraints = [
            models.CheckConstraint(condition=Q(day_of_week__gte=0, day_of_week__lte=6), name="working_hours_valid_day"),
            models.UniqueConstraint(fields=["location", "day_of_week"], name="working_hours_location_day_uniq"),
        ]

    def __str__(self):
        return f"{self.location} - day {self.day_of_week}"


class LocationImage(UUIDModel):
    location = models.ForeignKey(WorkshopLocation, on_delete=models.CASCADE, related_name="images")
    image_url = models.TextField()
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "location_images"
        ordering = ["sort_order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["location"], condition=Q(is_primary=True), name="location_images_one_primary"
            ),
        ]

    def __str__(self):
        return self.image_url


class LocationService(UUIDTimeStampedModel):
    """Pricing/availability of a catalog service at a specific location."""

    location = models.ForeignKey(WorkshopLocation, on_delete=models.CASCADE, related_name="location_services")
    service = models.ForeignKey("catalog.Service", on_delete=models.PROTECT, related_name="location_services")
    display_name = models.CharField(max_length=255, null=True, blank=True)
    price_type = models.CharField(max_length=10, choices=PriceType.choices, default=PriceType.NEGOTIABLE)
    price_from = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_to = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "location_services"
        indexes = [
            models.Index(fields=["location"], name="loc_services_location_idx"),
            models.Index(fields=["service"], name="loc_services_service_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["location", "service"], name="location_services_location_service_uniq"),
            models.CheckConstraint(condition=Q(price_type__in=PriceType.values), name="location_services_valid_price_type"),
            models.CheckConstraint(
                condition=Q(price_from__isnull=True) | Q(price_from__gte=Decimal("0")),
                name="location_services_price_from_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(price_to__isnull=True) | Q(price_to__gte=Decimal("0")),
                name="location_services_price_to_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(price_from__isnull=True) | Q(price_to__isnull=True) | Q(price_to__gte=F("price_from")),
                name="location_services_valid_price_range",
            ),
        ]

    def __str__(self):
        return self.display_name or self.service.name


class Favorite(models.Model):
    pk = models.CompositePrimaryKey("user", "location")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    location = models.ForeignKey(WorkshopLocation, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorites"

    def __str__(self):
        return f"{self.user} - {self.location}"
