"""Location search: keyword, geo, and AI-assisted.

All search paths converge on `LocationService` rows (a catalog service offered
at a workshop location), which are then grouped per location and ranked.
"""

import logging
from typing import Optional

from apps.common.geo import haversine_km
from apps.workshops.enums import LocationStatus, WorkshopStatus
from apps.workshops.models import LocationService
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

from .ai_client import OpenAIClient
from .prompt_builder import build_ai_prompt

logger = logging.getLogger(__name__)


def _base_offering_queryset():
    return (
        LocationService.objects.select_related(
            "location", "location__workshop", "service", "service__category"
        )
        .filter(
            is_available=True,
            location__status=LocationStatus.ACTIVE,
            location__workshop__status=WorkshopStatus.APPROVED,
            location__workshop__deleted_at__isnull=True,
        )
    )


def _keyword_filter(keywords, services):
    q = Q()
    for name in services or []:
        q |= Q(service__name__iexact=name)
    for kw in keywords or []:
        q |= Q(service__name__icontains=kw)
        q |= Q(service__description__icontains=kw)
        q |= Q(service__aliases__alias__icontains=kw)
        q |= Q(display_name__icontains=kw)
    return q


def _group_by_location(offerings, *, user_lat=None, user_lng=None, radius_km=None):
    """Collapse offerings into one entry per location, keeping cheapest price."""
    grouped: dict[str, dict] = {}
    for off in offerings:
        loc = off.location
        distance = None
        if user_lat is not None and user_lng is not None:
            distance = round(haversine_km(user_lat, user_lng, loc.latitude, loc.longitude), 2)
            if radius_km is not None and distance > radius_km:
                continue

        key = str(loc.id)
        entry = grouped.get(key)
        if entry is None:
            grouped[key] = {
                "location_id": loc.id,
                "workshop_id": loc.workshop_id,
                "workshop_name": loc.workshop.name,
                "premium": loc.workshop.premium,
                "location_name": loc.name,
                "address": loc.address,
                "phone": loc.phone,
                "rating": float(loc.rating),
                "review_count": loc.review_count,
                "latitude": float(loc.latitude),
                "longitude": float(loc.longitude),
                "distance_km": distance,
                "matched_services": [off.service.name],
                "price_from": off.price_from,
            }
        else:
            entry["matched_services"].append(off.service.name)
            if off.price_from is not None and (
                entry["price_from"] is None or off.price_from < entry["price_from"]
            ):
                entry["price_from"] = off.price_from
    return list(grouped.values())


def _rank(results):
    def key(item):
        return (
            0 if item["premium"] else 1,
            item["distance_km"] if item["distance_km"] is not None else float("inf"),
            -item["rating"],
            -item["review_count"],
        )

    results.sort(key=key)
    return results


def keyword_search(*, keywords, services=None, user_lat=None, user_lng=None, radius_km=None):
    offerings = _base_offering_queryset().filter(_keyword_filter(keywords, services)).distinct()
    results = _group_by_location(offerings, user_lat=user_lat, user_lng=user_lng, radius_km=radius_km)
    return _rank(results)


def nearby_search(*, service_id=None, category_id=None, user_lat, user_lng, radius_km=10):
    offerings = _base_offering_queryset()
    if service_id:
        offerings = offerings.filter(service_id=service_id)
    if category_id:
        offerings = offerings.filter(service__category_id=category_id)
    results = _group_by_location(offerings, user_lat=user_lat, user_lng=user_lng, radius_km=radius_km)
    return _rank(results)


class AISearchService:
    CACHE_TIMEOUT = getattr(settings, "AI_SEARCH_CACHE_TIMEOUT", 60 * 60)

    def __init__(self, client: Optional[OpenAIClient] = None):
        self.client = client or OpenAIClient()

    def ai_analyze(self, query: str) -> dict:
        cache_key = f"ai_analysis:{query}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        response = self.client.analyze(build_ai_prompt(query))
        result = {
            "intent": response.get("intent", "unknown"),
            "vehicle_system": response.get("vehicle_system", ""),
            "services": response.get("services", []),
            "keywords": response.get("keywords", []),
            "summary": response.get("summary", ""),
        }
        cache.set(cache_key, result, timeout=self.CACHE_TIMEOUT)
        return result

    def search(self, query: str, *, user_lat=None, user_lng=None, radius_km=None) -> dict:
        analysis = self.ai_analyze(query)
        results = keyword_search(
            keywords=analysis["keywords"] or [query],
            services=analysis["services"],
            user_lat=user_lat,
            user_lng=user_lng,
            radius_km=radius_km,
        )
        return {
            "ai": {
                "summary": analysis["summary"],
                "vehicle_system": analysis["vehicle_system"],
                "recommended_services": analysis["services"],
            },
            "results": results,
        }
