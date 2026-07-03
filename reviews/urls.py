from django.urls import path
from reviews.views import (
    create_review, 
    list_reviews, 
    delete_review,
    admin_reviews_list,
    admin_delete_review,
)

urlpatterns = [
    path('workshops/<uuid:workshop_id>/reviews/', list_reviews),
    path('workshops/<uuid:workshop_id>/reviews/create/', create_review),
    path('reviews/<uuid:review_id>/delete/', delete_review),
    
    # Admin endpoints
    path('admin/reviews/', admin_reviews_list),
    path('admin/reviews/<uuid:review_id>/delete/', admin_delete_review),
]