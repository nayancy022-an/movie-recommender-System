from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Movies ----
class MovieOut(BaseModel):
    id: int
    tmdb_id: Optional[int] = None
    title: str
    genres: str
    overview: str
    poster_path: Optional[str] = None
    release_year: Optional[int] = None

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    movie: MovieOut
    score: float


# ---- Ratings ----
class RatingCreate(BaseModel):
    movie_id: int
    rating: float


class RatingOut(BaseModel):
    id: int
    movie_id: int
    rating: float

    class Config:
        from_attributes = True


# ---- Watchlist ----
class WatchlistCreate(BaseModel):
    movie_id: int


class WatchlistOut(BaseModel):
    id: int
    movie: MovieOut
    added_at: datetime

    class Config:
        from_attributes = True
