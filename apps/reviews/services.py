"""Review write logic with denormalised rating maintenance."""

from apps.common.exceptions import ApplicationError
from apps.workshops.models import WorkshopLocation
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count

from .models import Review


def _recalculate_location_rating(location: WorkshopLocation) -> None:
    agg = location.reviews.aggregate(avg=Avg("rating"), count=Count("id"))
    location.rating = round(agg["avg"] or 0, 2)
    location.review_count = agg["count"] or 0
    location.save(update_fields=["rating", "review_count", "updated_at"])


@transaction.atomic
def create_review(*, user, location: WorkshopLocation, rating: int, comment: str = "") -> Review:
    try:
        review = Review.objects.create(user=user, location=location, rating=rating, comment=comment)
    except IntegrityError:
        raise ApplicationError("Siz bu filialga oldin sharh qoldirgansiz.")
    _recalculate_location_rating(location)
    return review


@transaction.atomic
def delete_review(*, review: Review) -> None:
    location = review.location
    review.delete()
    _recalculate_location_rating(location)
