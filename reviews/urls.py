from django.urls import path
from reviews.views import create_review, list_reviews, delete_review

urlpatterns = [
    path('workshops/<int:workshop_id>/reviews/', create_review, name='create-review'),
    path('workshops/<int:workshop_id>/reviews/list/', list_reviews, name='list-reviews'),
    path('reviews/<int:review_id>/', delete_review),
]
