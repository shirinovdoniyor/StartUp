from django.db import models

from django.db import models

class Workshop(models.Model):
    name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    services = models.TextField(help_text="Comma-separated service list")
    phone = models.CharField(max_length=20)
    rating = models.FloatField(default=0)
    premium = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    workshop = models.ForeignKey(Workshop, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.workshop.name}"
