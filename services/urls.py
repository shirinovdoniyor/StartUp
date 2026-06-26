from django.urls import path
from .views import (
    search_services,
    workshop_service_create,
    workshop_service_delete,
    workshop_service_update,
    workshop_services,
)

urlpatterns = [
    path('workshop/services/create/', workshop_service_create),
    path('workshop/<int:workshop_id>/services/', workshop_services),
    path('workshop/services/<int:pk>/delete/', workshop_service_delete),
    path('workshop/services/update/<int:pk>/', workshop_service_update),
    path('search/', search_services),
]