from django.db import models


class WorkshopStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    BLOCKED = "BLOCKED", "Blocked"


class LocationStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class PriceType(models.TextChoices):
    FIXED = "FIXED", "Fixed"
    RANGE = "RANGE", "Range"
    NEGOTIABLE = "NEGOTIABLE", "Negotiable"
