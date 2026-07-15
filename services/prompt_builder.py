"""Build prompts for the OpenAI client used by AI semantic search.

This module centralizes prompt construction so the model is constrained
to return structured JSON only.
"""

from typing import List


def build_ai_prompt(query: str) -> str:
    """Return a system+user style prompt instructing the model to output
    JSON only. The schema includes: intent, vehicle_system, services,
    keywords, summary.
    """

    prompt = (
        "You are an assistant that extracts user intent and automotive symptoms. "
        "Return JSON only (no explanation, no markdown). Follow this schema:\n"
        "{\n  \"intent\": \"...\",\n  \"vehicle_system\": \"...\",\n  "
        "\"services\": ["""
        + "\"...\"" + "],\n  \"keywords\": [\"...\"],\n  \"summary\": \"...\"\n}\n"
        "Constraints:\n"
        "- Do NOT invent workshop names or phone numbers.\n"
        "- Keep values short.\n"
        "- 'intent' should be one of: service_search, info_request, unknown.\n"
        "- 'services' may contain short service names that a human would search.\n"
        "- 'keywords' should be concise keywords extracted from the query.\n"
        "Now analyze the following user query and output JSON only. Query: '"
        + query.replace("\n", " ")
        + "'"
    )

    return prompt
