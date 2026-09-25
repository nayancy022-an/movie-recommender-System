import os
import pickle

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/recommend", tags=["recommend"])

_INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "movies.index")
_META_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "movies_meta.pkl")

_index = None
_meta_df = None


def _load_index():
    """Lazy-load the FAISS index + metadata built by app/ml/build_index.py.

    faiss is imported here (not at module level) so the rest of the API
    (auth, movies, watchlist) still boots even before ML deps are installed
    or the index has been built.
    """
    global _index, _meta_df
    if _index is None:
        try:
            import faiss
        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="faiss-cpu not installed. Run: pip install -r requirements.txt",
            )
        if not os.path.exists(_INDEX_PATH):
            raise HTTPException(
                status_code=503,
                detail="Recommendation index not built yet. Run: python -m app.ml.build_index",
            )
        _index = faiss.read_index(_INDEX_PATH)
        with open(_META_PATH, "rb") as f:
            meta = pickle.load(f)
        _meta_df = meta["df"]
    return _index, _meta_df


@router.get("/{movie_id}", response_model=list[schemas.RecommendationOut])
def content_based_recommend(movie_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    """Content-based: nearest neighbours in embedding space (Sentence-BERT + FAISS)."""
    index, meta_df = _load_index()

    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie or movie.tmdb_id is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    row = meta_df[meta_df["tmdb_id"] == movie.tmdb_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Movie not present in recommendation index")
    row_idx = row.index[0]

    query_vec = index.reconstruct(int(row_idx)).reshape(1, -1)
    scores, indices = index.search(query_vec, top_k + 1)  # +1 because the movie itself will match

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == row_idx or idx == -1:
            continue
        tmdb_id = int(meta_df.iloc[idx]["tmdb_id"])
        db_movie = db.query(models.Movie).filter(models.Movie.tmdb_id == tmdb_id).first()
        if db_movie:
            results.append(schemas.RecommendationOut(movie=db_movie, score=float(score)))
        if len(results) >= top_k:
            break
    return results


@router.get("/for-you/list", response_model=list[schemas.RecommendationOut])
def personalized_recommend(user_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    """
    Hybrid: average the content-based embeddings of movies the user rated >= 4,
    weighted by their rating, then find nearest neighbours. Falls back to
    popularity (most-rated) if the user has no ratings yet (cold start).
    """
    index, meta_df = _load_index()

    ratings = (
        db.query(models.Rating)
        .filter(models.Rating.user_id == user_id, models.Rating.rating >= 4)
        .all()
    )

    if not ratings:
        top_movies = db.query(models.Movie).limit(top_k).all()
        return [schemas.RecommendationOut(movie=m, score=0.0) for m in top_movies]

    vectors = []
    weights = []
    liked_tmdb_ids = set()
    for r in ratings:
        movie = db.query(models.Movie).filter(models.Movie.id == r.movie_id).first()
        if not movie or movie.tmdb_id is None:
            continue
        row = meta_df[meta_df["tmdb_id"] == movie.tmdb_id]
        if row.empty:
            continue
        row_idx = row.index[0]
        vectors.append(index.reconstruct(int(row_idx)))
        weights.append(r.rating)
        liked_tmdb_ids.add(movie.tmdb_id)

    if not vectors:
        top_movies = db.query(models.Movie).limit(top_k).all()
        return [schemas.RecommendationOut(movie=m, score=0.0) for m in top_movies]

    vectors = np.array(vectors, dtype="float32")
    weights = np.array(weights, dtype="float32").reshape(-1, 1)
    user_vector = (vectors * weights).sum(axis=0) / weights.sum()
    user_vector = (user_vector / np.linalg.norm(user_vector)).reshape(1, -1)

    scores, indices = index.search(user_vector, top_k + len(liked_tmdb_ids))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        tmdb_id = int(meta_df.iloc[idx]["tmdb_id"])
        if tmdb_id in liked_tmdb_ids:
            continue
        db_movie = db.query(models.Movie).filter(models.Movie.tmdb_id == tmdb_id).first()
        if db_movie:
            results.append(schemas.RecommendationOut(movie=db_movie, score=float(score)))
        if len(results) >= top_k:
            break
    return results
