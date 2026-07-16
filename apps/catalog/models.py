from apps.common.models import UUIDModel, UUIDTimeStampedModel
from django.db import models


class Category(UUIDTimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.TextField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "categories"
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Service(UUIDTimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "services"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServiceAlias(UUIDModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=255)

    class Meta:
        db_table = "service_aliases"
        constraints = [
            models.UniqueConstraint(fields=["service", "alias"], name="service_aliases_service_alias_uniq"),
        ]

    def __str__(self):
        return self.alias
