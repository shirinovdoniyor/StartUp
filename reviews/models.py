from django.db import models
from django.contrib.auth import get_user_model
from apps.models import Workshop

User = get_user_model()


class Review(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.workshop.name}"