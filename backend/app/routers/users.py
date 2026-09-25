from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(tags=["users"])


# ---- Ratings ----
@router.post("/ratings", response_model=schemas.RatingOut)
def rate_movie(
    payload: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    movie = db.query(models.Movie).filter(models.Movie.id == payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing = (
        db.query(models.Rating)
        .filter(models.Rating.user_id == current_user.id, models.Rating.movie_id == payload.movie_id)
        .first()
    )
    if existing:
        existing.rating = payload.rating
        db.commit()
        db.refresh(existing)
        return existing

    rating = models.Rating(user_id=current_user.id, movie_id=payload.movie_id, rating=payload.rating)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("/ratings/me", response_model=list[schemas.RatingOut])
def my_ratings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Rating).filter(models.Rating.user_id == current_user.id).all()


# ---- Watchlist ----
@router.post("/watchlist", response_model=schemas.WatchlistOut)
def add_to_watchlist(
    payload: schemas.WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    movie = db.query(models.Movie).filter(models.Movie.id == payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing = (
        db.query(models.WatchlistItem)
        .filter(models.WatchlistItem.user_id == current_user.id, models.WatchlistItem.movie_id == payload.movie_id)
        .first()
    )
    if existing:
        return existing

    item = models.WatchlistItem(user_id=current_user.id, movie_id=payload.movie_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/watchlist/me", response_model=list[schemas.WatchlistOut])
def my_watchlist(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.WatchlistItem).filter(models.WatchlistItem.user_id == current_user.id).all()


@router.delete("/watchlist/{movie_id}")
def remove_from_watchlist(
    movie_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    item = (
        db.query(models.WatchlistItem)
        .filter(models.WatchlistItem.user_id == current_user.id, models.WatchlistItem.movie_id == movie_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Not in watchlist")
    db.delete(item)
    db.commit()
    return {"detail": "Removed"}


@router.get("/users/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user
