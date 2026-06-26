import uuid

from django.db import models
from apps.models import Workshop

class WorkshopService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.workshop.name} - {self.service_name}"