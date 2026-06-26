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
    path('workshop/<uuid:workshop_id>/services/', workshop_services),
    path('workshop/services/<uuid:pk>/delete/', workshop_service_delete),
    path('workshop/services/update/<uuid:pk>/', workshop_service_update),
    path('search/', search_services),
]