import uuid

from django.db import models
from apps.models import Workshop

class Service(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )
    
    description = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name



class WorkshopService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="workshops",
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.workshop.name} - {self.service.name}"