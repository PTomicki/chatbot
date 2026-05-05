from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
import requests
import json
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import os
import csv
from loader import DataLoader
import psycopg2 



df_cache = None
model = SentenceTransformer("all-MiniLM-L6-v2")

API_KEY = os.getenv("OPENROUTER_API_KEY")

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()

# =========================
# SCHEMA LOADER
# =========================

def load_schema():
    with open(CONFIG["schema_path"], "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_df(df, schema):
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]

    reverse_map = {}

    for standard_key, real_col in schema.items():
        if real_col in df.columns:
            reverse_map[real_col] = standard_key

    df = df.rename(columns=reverse_map)

    return df


def denormalize_df(df, schema):
    """Konwertuje z powrotem angielskie nazwy kolumn na polskie dla frontendu"""
    df = df.copy()
    
    # Odwrotne mapowanie: z angielskiego na polskie
    forward_map = {}
    for standard_key, real_col in schema.items():
        if standard_key in df.columns:
            forward_map[standard_key] = real_col
    
    df = df.rename(columns=forward_map)
    return df


# =========================
# DATA LOADER (FIXED ONLY CRITICAL PART)
# =========================

def load_data():
    return DataLoader.load(CONFIG)


# =========================
# LOAD DATABASE
# =========================
def get_col(df, schema, key, fallback=None):
    """
    Zwraca realną nazwę kolumny na podstawie schemy.
    """
    real = schema.get(key, fallback)
    if real in df.columns:
        return real
    return None

def load_database():
    global df_cache

    df = DataLoader.load(CONFIG)

    schema = load_schema()
    df = normalize_df(df, schema)

    df.columns = df.columns.str.strip()

    # SAFE DEFAULTS (ważne żeby nie crashowało)
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).astype(int)

    if "year" not in df.columns:
        df["year"] = 0

    if "mileage" not in df.columns:
        df["mileage"] = 0

    # embedding only if possible
    if all(x in df.columns for x in ["brand", "model", "year"]):
        df["text"] = (
            df["brand"].astype(str) + " " +
            df["model"].astype(str) + " " +
            df["year"].astype(str)
        )

        print("🔄 Encoding embeddings...")
        df["embedding"] = list(model.encode(df["text"].tolist()))

    else:
        # fallback żeby system nie padł
        df["text"] = df.astype(str).agg(" ".join, axis=1)
        df["embedding"] = list(model.encode(df["text"].tolist()))

    df_cache = df
    print("✅ DB loaded:", len(df))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_database()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================
# AI (UNCHANGED)
# =========================

def ai_parse(query: str):
    df = df_cache

    brands = df["brand"].dropna().unique().tolist()
    models = df["model"].dropna().unique().tolist()

    system = "You are strict JSON extractor."

    prompt = f"""
You are an intelligent intent extraction system for a car marketplace.

Your job is to UNDERSTAND user intent and convert it into structured filters.

DO NOT guess. Only extract what is clearly stated.

DATABASE CONTEXT:
- brands: {brands}
- models: {models}

OUTPUT JSON:
{{
  "brand": null,
  "model": null,
  "price_min": null,
  "price_max": null,
  "year_min": null,
  "year_max": null
}}

YEAR UNDERSTANDING:
- "z 2020 roku" → year_min = 2020, year_max = 2020
- "po 2020" → year_min = 2021
- "młodsze niż 2020" → year_min = 2021
- "starsze niż 2020" → year_max = 2019
- "do 2020" → year_max = 2020

KM UNDERSTANDING:
- "do 50 000 km" → km_max = 50000
- "poniżej 100k" → km_max = 100000
- "powyżej 80k" → km_min = 80000

STRICT RULES:
- never guess
- only extract

USER QUERY:
{query}
"""

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
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0
            },
            timeout=15
        )

        raw = res.json()["choices"][0]["message"]["content"]

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        return {}

    except Exception as e:
        print("AI ERROR:", e)
        return {}


# =========================
# EMBEDDING SEARCH (UNCHANGED)
# =========================

def embedding_search(query, df, top_k=30):
    query_vec = model.encode([query])

    df = df.copy()

    embeddings = np.vstack(df["embedding"].values)

    scores = cosine_similarity(query_vec, embeddings)[0]

    df["score"] = scores

    return df.sort_values("score", ascending=False).head(top_k)


# =========================
# FILTERS (UNCHANGED LOGIC)
# =========================

def apply_filters(df, filters):
    df = df.copy()

    for key, value in filters.items():

        if value is None or value == "":
            continue

        if key == "brand":
            df = df[df["brand"].str.lower() == str(value).lower().strip()]

        elif key == "model":
            df = df[df["model"].str.lower().str.contains(str(value).lower(), na=False)]

        elif key == "price_max":
            df = df[df["price"] <= float(value)]

        elif key == "price_min":
            df = df[df["price"] >= float(value)]

        elif key == "year_min":
            df = df[df["year"] >= int(value)]

        elif key == "year_max":
            df = df[df["year"] <= int(value)]

        elif key == "km_min":
            df = df[df["mileage"] >= int(value)]

        elif key == "km_max":
            df = df[df["mileage"] <= int(value)]

    return df


def validate_ai(ai):
    y_min = ai.get("year_min")
    y_max = ai.get("year_max")

    if y_min is not None and y_max is not None:
        if y_min > y_max:
            ai["year_min"], ai["year_max"] = y_max, y_min

    return ai


# =========================
# LOGGING (UNCHANGED)
# =========================

def log_search(query, ai):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().isoformat()

    csv_file = "logs/searches.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp", "query", "brand", "model",
                "year_min", "year_max",
                "price_min", "price_max",
                "km_min", "km_max"
            ])

        writer.writerow([
            timestamp,
            query,
            ai.get("brand"),
            ai.get("model"),
            ai.get("year_min"),
            ai.get("year_max"),
            ai.get("price_min"),
            ai.get("price_max"),
            ai.get("km_min"),
            ai.get("km_max"),
        ])


# =========================
# API
# =========================

@app.get("/chat")
async def chat(query: str = Query(...)):

    ai = ai_parse(query)
    ai = validate_ai(ai)

    log_search(query, ai)

    df = df_cache.copy()

    df = apply_filters(df, ai)
    df = embedding_search(query, df, top_k=30)

    # Usuń kolumny techniczne przed denormalizacją
    df = df.drop(columns=["embedding", "text", "score"], errors="ignore")
    
    # Konwertuj nazwy kolumn z angielskich na polskie
    schema = load_schema()
    df = denormalize_df(df, schema)
    
    cars = df.to_dict(orient="records")

    return {
        "text": f"Znaleziono {len(cars)} aut.",
        "count": len(cars),
        "cars": cars,
        "ai": ai
    }


# =========================
# RUN
# =========================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )