def get_prompt(query: str, context: dict = None) -> str:

    context = context or {}

    brands = context.get("brands", [])
    models = context.get("models", [])

    return f"""
You are an intelligent intent extraction system for a car marketplace.

Extract structured filters ONLY.

BRANDS:
{brands}

MODELS:
{models}

OUTPUT JSON:
{{
  "brand": null,
  "model": null,
  "price_min": null,
  "price_max": null,
  "year_min": null,
  "year_max": null,
  "damage": null,
  "km_min": null,
  "km_max": null
}}

RULES:
- never guess
- return ONLY JSON

USER QUERY:
{query}
"""