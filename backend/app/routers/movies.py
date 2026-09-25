from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/search", response_model=list[schemas.MovieOut])
def search_movies(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    like = f"%{q}%"
    return db.query(models.Movie).filter(models.Movie.title.ilike(like)).limit(25).all()


@router.get("/{movie_id}", response_model=schemas.MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("", response_model=list[schemas.MovieOut])
def list_movies(genre: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(models.Movie)
    if genre:
        query = query.filter(models.Movie.genres.ilike(f"%{genre}%"))
    return query.limit(limit).all()
