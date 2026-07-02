from django.urls import path
from .views import (
    search_services,
    workshop_service_create,
    workshop_service_delete,
    workshop_service_update,
    workshop_services,
    admin_problems_list,
    admin_problems_create,
    admin_problems_update,
    admin_problems_delete,
)

urlpatterns = [
    path('workshop/services/create/', workshop_service_create),
    path('workshop/<uuid:workshop_id>/services/', workshop_services),
    path('workshop/services/<uuid:pk>/delete/', workshop_service_delete),
    path('workshop/services/update/<uuid:pk>/', workshop_service_update),
    path('search/', search_services),
    
    # Admin Problems endpoints
    path('admin/problems/', admin_problems_list),
    path('admin/problems/create/', admin_problems_create),
    path('admin/problems/<uuid:problem_id>/update/', admin_problems_update),
    path('admin/problems/<uuid:problem_id>/delete/', admin_problems_delete),
]