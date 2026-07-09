import uuid

from django.db import models


class Workshop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    premium = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='workshops/', null=True, blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True,)

    def __str__(self):
        return self.name


