from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('workshop', 'Workshop'),
    )
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
