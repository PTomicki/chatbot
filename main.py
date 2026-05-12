from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import csv
import json
from datetime import datetime

from database.loader import load_database, get_cache
from database.filters import apply_filters
from database.embeddings import embedding_search
from config import get_config
from ai.parser import ai_parse
from utils.validators import validate_ai

CONFIG = get_config()

# =========================
# LOGGING (na razie inline)
# =========================
def log_search(query, ai):
    os.makedirs("logs", exist_ok=True)

    file = "logs/searches.csv"
    exists = os.path.isfile(file)

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not exists:
            writer.writerow([
                "timestamp", "query",
                "brand", "model",
                "year_min", "year_max",
                "price_min", "price_max",
                "km_min", "km_max"
            ])

        writer.writerow([
            datetime.now().isoformat(),
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
# FASTAPI
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_database(CONFIG)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ENDPOINT
# =========================
@app.get("/chat")
async def chat(query: str = Query(...)):

    df = get_cache().copy()

    # =========================
    # AI
    # =========================
    ai = ai_parse(query, {
        "brands": df["brand"].dropna().unique().tolist(),
        "models": df["model"].dropna().unique().tolist()
    })

    ai = validate_ai(ai)

    log_search(query, ai)

    # =========================
    # PIPELINE
    # =========================
    df = apply_filters(df, ai)

    df = embedding_search(query, df, top_k=30)

    df = df.drop(columns=["embedding", "text", "score"], errors="ignore")

    return {
        "text": f"Znaleziono {len(df)} aut.",
        "count": len(df),
        "cars": df.to_dict(orient="records"),
        "ai": ai
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)