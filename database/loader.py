import os
import json
import pandas as pd
import psycopg2
import requests

from database.normalizer import normalize_df

# =========================
# GLOBAL CACHE
# =========================
df_cache = None


def get_cache():
    global df_cache
    return df_cache


# =========================
# SCHEMA LOADER
# =========================
def load_schema(config):
    schema_path = config.get("schema_path", "schema.json")

    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# MAIN LOADER
# =========================
def load_database(config):
    global df_cache

    source = config.get("data_source")

    if source == "csv":
        df = _load_csv(config)

    elif source == "postgres":
        df = _load_postgres(config)

    elif source == "api":
        df = _load_api(config)

    else:
        raise Exception(f"Unknown data source: {source}")

    # =========================
    # NORMALIZATION STEP (IMPORTANT)
    # =========================
    schema = load_schema(config)

    df.columns = df.columns.str.lower().str.strip()

    df = normalize_df(df, schema)

# =========================
# CLEAN NUMERIC COLUMNS
# =========================

    numeric_cols = ["price", "year", "mileage"]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = (
                df[col]
                .astype(str)
                .str.replace(" ", "", regex=False)
                .str.replace(",", "", regex=False)
            )

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            df[col] = df[col].fillna(0).astype(int)

    df_cache = df


# =========================
# CSV
# =========================
def _load_csv(config):
    path = config.get("csv_path")

    df = pd.read_csv(
        path,
        sep=None,
        engine="python",
        encoding="utf-8-sig"
    )

    return df


# =========================
# POSTGRES
# =========================
def _load_postgres(config):
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")

    conn = psycopg2.connect(DATABASE_URL)

    query = config["query"]

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =========================
# API
# =========================
def _load_api(config):
    url = config["url"]

    r = requests.get(url)

    return pd.DataFrame(r.json())