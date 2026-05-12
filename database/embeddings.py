import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


# =========================
# BUILD EMBEDDINGS
# =========================
def build_embeddings(df, text_column="text"):
    """
    Tworzy embeddingi dla DF
    """
    if text_column not in df.columns:
        return df

    df = df.copy()
    df["embedding"] = list(model.encode(df[text_column].astype(str).tolist()))
    return df


# =========================
# SEARCH
# =========================
def embedding_search(query, df, top_k=30):

    if "embedding" not in df.columns:
        return df.head(top_k)

    embeddings = df["embedding"].dropna().tolist()

    if len(embeddings) == 0:
        return df.head(top_k)

    query_vec = model.encode([query])
    matrix = np.vstack(embeddings)

    scores = cosine_similarity(query_vec, matrix)[0]

    df = df.copy()
    df["score"] = scores

    return df.sort_values("score", ascending=False).head(top_k)