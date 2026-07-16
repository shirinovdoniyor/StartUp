from apps.common.models import UUIDTimeStampedModel
from django.conf import settings
from django.db import models
from django.db.models import Q


class RequestStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class ServiceRequest(UUIDTimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_requests",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    status = models.CharField(max_length=11, choices=RequestStatus.choices, default=RequestStatus.OPEN)

    class Meta:
        db_table = "service_requests"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user"], name="requests_user_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(status__in=RequestStatus.values), name="service_requests_valid_status"),
        ]

    def __str__(self):
        return self.title
