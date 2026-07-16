"""Prompt construction for AI semantic search."""


def build_ai_prompt(query: str) -> str:
    schema = (
        '{\n  "intent": "...",\n  "vehicle_system": "...",\n  '
        '"services": ["..."],\n  "keywords": ["..."],\n  "summary": "..."\n}'
    )
    return (
        "You are an assistant that extracts user intent and automotive symptoms. "
        "Return JSON only (no explanation, no markdown). Follow this schema:\n"
        f"{schema}\n"
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
