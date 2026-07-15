from django.test import TestCase
from services.ai_search import AISearchService
from services.ai_client import OpenAIClient
from services.models import Service, Problem, WorkshopService
from apps.models import Workshop


class AISearchTests(TestCase):
    def setUp(self):
        self.workshop = Workshop.objects.create(
            name="Turbo Motors",
            owner_name="Owner",
            address="Some address",
            phone="123",
            rating=4.5,
            rating_count=10,
            premium=True,
        )

        self.service = Service.objects.create(name="Oil Change")

        self.ws = WorkshopService.objects.create(
            workshop=self.workshop,
            service=self.service,
            price=100.00,
        )

    def test_simple_named_query_uses_db_search(self):
        service = AISearchService()
        res = service.search("Oil Change")
        # AI block should be empty since this is a simple named query
        self.assertIn("ai", res)
        self.assertEqual(res["ai"]["recommended_services"], [])
        self.assertTrue(len(res["results"]) >= 1)

    def test_natural_language_calls_ai_and_returns_results(self):
        # Patch OpenAIClient.analyze to avoid network call
        def fake_analyze(self, prompt):
            return {
                "intent": "service_search",
                "vehicle_system": "Engine",
                "services": ["Oil Change"],
                "keywords": ["oil", "leak"],
                "summary": "Oil leak or low oil may cause engine problems."
            }

        OpenAIClient.analyze = fake_analyze

        service = AISearchService()
        res = service.search("My engine is leaking oil and running hot")
        self.assertIn("ai", res)
        self.assertEqual(res["ai"]["vehicle_system"], "Engine")
        self.assertTrue(len(res["results"]) >= 1)
