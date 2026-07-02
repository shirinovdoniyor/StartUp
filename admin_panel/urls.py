from django.urls import path
from .views import (
    admin_dashboard, 
    admin_users, 
    admin_user_detail, 
    admin_user_update, 
    admin_workshops,
    admin_workshop_detail, 
    admin_workshop_delete, 
    admin_workshop_update,
    admin_search,
)

urlpatterns = [
    path("dashboard/", admin_dashboard, name="admin-dashboard"),
    path("users/", admin_users),
    path("users/<uuid:id>/", admin_user_detail),

    path("users/<uuid:id>/update/", admin_user_update),
    path("workshops/", admin_workshops),
    path("workshops/<uuid:id>/", admin_workshop_detail),
    path("workshops/<uuid:id>/delete/", admin_workshop_delete),
    path("workshops/<uuid:id>/update/",admin_workshop_update,name="admin-workshop-update",),
    
    # Admin search
    path("search/", admin_search),
]

