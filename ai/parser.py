import os
import json
import re
import requests

from ai.prompts import get_prompt   # 👈 dynamiczne prompty


API_KEY = os.getenv("OPENROUTER_API_KEY")


# =========================
# MAIN PARSER FUNCTION
# =========================
def ai_parse(query: str, context: dict = None) -> dict:
    """
    Zamienia tekst usera → structured filters (JSON)
    """

    prompt = get_prompt(query, context or {})

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a strict JSON extractor. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            },
            timeout=15
        )

        raw = res.json()["choices"][0]["message"]["content"]

        # =========================
        # SAFE JSON EXTRACTION
        # =========================
        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if match:
            return json.loads(match.group(0))

        return {}

    except Exception as e:
        print("AI PARSER ERROR:", e)
        return {}