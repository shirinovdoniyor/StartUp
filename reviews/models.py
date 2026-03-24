from django.db import models

class Review(models.Model):
    workshop = models.ForeignKey('apps.Workshop', on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()


    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_name} - {self.workshop.name}"