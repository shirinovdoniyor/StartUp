"""Service layer for AI-driven semantic search.

This module decides whether a query should use traditional DB search
or call the OpenAI client to extract intent/keywords, then performs
an ORM search and ranking.
"""

from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
from django.db.models import Q
from django.conf import settings
from .ai_client import OpenAIClient
from .prompt_builder import build_ai_prompt
from .models import Service, WorkshopService, Workshop
import logging

logger = logging.getLogger(__name__)


class AISearchService:
    CACHE_TIMEOUT = getattr(settings, "AI_SEARCH_CACHE_TIMEOUT", 60 * 60)

    def __init__(self, client: Optional[OpenAIClient] = None):
        self.client = client or OpenAIClient()

    def is_simple_named_query(self, query: str) -> bool:
        # Heuristic: short queries (<=3 words) that match a Service or Workshop name
        words = [w for w in query.split() if w.strip()]
        if len(words) <= 3:
            # check service name exact or partial
            if Service.objects.filter(name__iexact=query).exists():
                return True
            if Workshop.objects.filter(name__iexact=query).exists():
                return True
        return False

    def build_db_queryset(self, keywords: List[str], recommended_services: List[str]) -> List[Dict]:
        # Search by service name, service description, service problems, workshop name/address
        service_q = Q()
        if recommended_services:
            service_q |= Q(service__name__in=recommended_services)

        for kw in keywords:
            service_q |= Q(service__name__icontains=kw)
            service_q |= Q(service__description__icontains=kw)
            service_q |= Q(service__problems__name__icontains=kw)

        workshop_q = Q()
        for kw in keywords:
            workshop_q |= Q(workshop__name__icontains=kw)
            workshop_q |= Q(workshop__address__icontains=kw)

        qs = (
            WorkshopService.objects
            .select_related("workshop", "service")
            .filter(service_q | workshop_q)
            .distinct()
        )

        results = []

        for ws in qs:
            w = ws.workshop
            results.append({
                "id": w.id,
                "name": w.name,
                "address": w.address,
                "phone": w.phone,
                "rating": w.rating,
                "rating_count": w.rating_count,
                "premium": w.premium,
                "matched_services": [ws.service.name],
                "price": ws.price,
                "latitude": w.latitude,
                "longitude": w.longitude,
            })

        return results

    def rank_results(self, results: List[Dict], recommended_services: List[str]) -> List[Dict]:
        # Ranking tuple: premium first, exact service match, rating, rating_count
        def rank_key(item: Dict) -> Tuple:
            exact = 0
            for s in recommended_services:
                if s in item.get("matched_services", []):
                    exact = 1
                    break
            return (
                0 if item.get("premium") else 1,  # premium first
                -exact,                              # exact match first
                -item.get("rating", 0),
                -item.get("rating_count", 0),
            )

        results.sort(key=rank_key)
        return results

    def ai_analyze(self, query: str) -> Dict:
        cache_key = f"ai_analysis:{query}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        prompt = build_ai_prompt(query)
        response = self.client.analyze(prompt)

        # Minimal validation of returned structure
        result = {
            "intent": response.get("intent", "unknown"),
            "vehicle_system": response.get("vehicle_system", ""),
            "services": response.get("services", []),
            "keywords": response.get("keywords", []),
            "summary": response.get("summary", ""),
        }

        cache.set(cache_key, result, timeout=self.CACHE_TIMEOUT)
        return result

    def search(self, query: str) -> Dict:
        """Main entry point.

        Decide traditional vs AI; return ai block and DB search results.
        """
        if self.is_simple_named_query(query):
            # Do a normal DB search by service/workshop name
            keywords = [query]
            recommended_services = []
            ai_block = {"summary": "", "vehicle_system": "", "recommended_services": []}
        else:
            analysis = self.ai_analyze(query)
            keywords = analysis.get("keywords") or []
            recommended_services = analysis.get("services") or []
            ai_block = {
                "summary": analysis.get("summary", ""),
                "vehicle_system": analysis.get("vehicle_system", ""),
                "recommended_services": recommended_services,
            }

        results = self.build_db_queryset(keywords, recommended_services)
        ranked = self.rank_results(results, recommended_services)

        return {
            "ai": ai_block,
            "results": ranked,
        }
