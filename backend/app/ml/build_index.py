"""
Offline script: reads movies from data/movies_sample.csv (or your own TMDB
export), builds embeddings, and writes a FAISS index + metadata to disk.

Run this once (and whenever your movie catalog changes):
    python -m app.ml.build_index

Swap data/movies_sample.csv with your real TMDB dataset (same columns:
tmdb_id,title,genres,overview,poster_path,release_year) to go from demo
data to your full catalog.
"""
import os
import pickle

import faiss
import numpy as np
import pandas as pd

from app.ml.embeddings import EmbeddingBackend

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "movies_sample.csv")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "movies.index")
META_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "movies_meta.pkl")


def build():
    df = pd.read_csv(DATA_PATH)
    df["genres"] = df["genres"].fillna("")
    df["overview"] = df["overview"].fillna("")
    combined_text = (df["title"] + ". " + df["genres"].str.replace("|", " ") + ". " + df["overview"]).tolist()

    backend = EmbeddingBackend()
    print(f"Using embedding backend: {backend.mode}")
    embeddings = backend.fit_transform(combined_text)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity via inner product on normalized vectors
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump({"df": df.reset_index(drop=True), "backend_mode": backend.mode}, f)

    print(f"Indexed {len(df)} movies -> {INDEX_PATH}")


if __name__ == "__main__":
    build()
