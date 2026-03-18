from django.db import models

from apps.models import Workshop


class Review(models.Model):
    workshop = models.ForeignKey(Workshop, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.workshop.name}"