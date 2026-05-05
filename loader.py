import pandas as pd
import psycopg2
import mysql.connector
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Ładuje zmienne środowiskowe z pliku .env

class DataLoader:

    @staticmethod
    def load(config):
        source = config.get("data_source")

        if source == "csv":
            return DataLoader._load_csv(config)

        elif source == "postgres":
            return DataLoader._load_postgres(config)

        elif source == "mysql":
            return DataLoader._load_mysql(config)

        elif source == "api":
            return DataLoader._load_api(config)

        else:
            raise Exception(f"Unknown data source: {source}")


    @staticmethod
    def _load_csv(config):
        path = config.get("csv_path")

        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
        return df


    @staticmethod
    def _load_postgres(config):
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)

        query = config["query"]
        df = pd.read_sql(query, conn)
        conn.close()
        return df


    @staticmethod
    def _load_mysql(config):
        conn = mysql.connector.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )

        query = config["query"]
        df = pd.read_sql(query, conn)
        conn.close()
        return df


    @staticmethod
    def _load_api(config):
        url = config["url"]
        r = requests.get(url)
        return pd.DataFrame(r.json())