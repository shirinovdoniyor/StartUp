from django.urls import path

from . import location_views, workshop_views

urlpatterns = [
    # Workshops
    path("", workshop_views.workshop_list, name="workshop-list"),
    path("create/", workshop_views.workshop_create, name="workshop-create"),
    path("<uuid:pk>/", workshop_views.workshop_detail, name="workshop-detail"),
    path("<uuid:pk>/update/", workshop_views.workshop_update, name="workshop-update"),
    path("<uuid:pk>/delete/", workshop_views.workshop_delete, name="workshop-delete"),
    # Locations (nested under workshop)
    path("<uuid:workshop_id>/locations/", location_views.location_list, name="location-list"),
    path("<uuid:workshop_id>/locations/create/", location_views.location_create, name="location-create"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/", location_views.location_detail, name="location-detail"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/update/", location_views.location_update, name="location-update"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/delete/", location_views.location_delete, name="location-delete"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/working-hours/", location_views.location_working_hours, name="location-working-hours"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/images/", location_views.location_add_image, name="location-add-image"),
    # Offerings (location services)
    path("<uuid:workshop_id>/locations/<uuid:location_id>/offerings/", location_views.offering_list, name="offering-list"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/offerings/create/", location_views.offering_create, name="offering-create"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/offerings/<uuid:offering_id>/update/", location_views.offering_update, name="offering-update"),
    path("<uuid:workshop_id>/locations/<uuid:location_id>/offerings/<uuid:offering_id>/delete/", location_views.offering_delete, name="offering-delete"),
]
