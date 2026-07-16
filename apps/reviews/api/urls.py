from django.urls import path

from . import views

urlpatterns = [
    path("locations/<uuid:location_id>/", views.location_reviews, name="location-reviews"),
    path("locations/<uuid:location_id>/create/", views.create_review, name="review-create"),
    path("<uuid:review_id>/delete/", views.delete_review, name="review-delete"),
]
