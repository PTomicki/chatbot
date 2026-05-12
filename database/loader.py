import os
import pandas as pd
import psycopg2
import requests


# =========================
# GLOBAL CACHE
# =========================
df_cache = None


def get_cache():
    global df_cache
    return df_cache


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

    df.columns = df.columns.str.lower().str.strip()

    df_cache = df

    print(f"✅ DATABASE LOADED: {len(df)} rows")

    return df


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