from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()

class Review(models.Model):
    workshop = models.ForeignKey('apps.Workshop', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now_add=True)
