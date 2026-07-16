from apps.common.models import UUIDTimeStampedModel
from django.conf import settings
from django.db import models
from django.db.models import Q


class Review(UUIDTimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    location = models.ForeignKey(
        "workshops.WorkshopLocation",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["location"], name="reviews_location_idx"),
            models.Index(fields=["user"], name="reviews_user_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="reviews_rating_1_5"),
            models.UniqueConstraint(fields=["user", "location"], name="reviews_user_location_uniq"),
        ]

    def __str__(self):
        return f"{self.user} - {self.location} ({self.rating})"
