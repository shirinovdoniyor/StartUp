import uuid

from django.conf import settings
from django.db import models


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workshop = models.ForeignKey(
        'apps.Workshop',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.workshop} ({self.rating}★)"