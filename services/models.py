from django.db import models
from apps.models import Workshop


class Problem(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return self.name

class WorkshopService(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='workshops')

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.workshop.name} - {self.service.name}"