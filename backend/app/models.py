from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)  # local id, maps to row index in embedding matrix
    tmdb_id = Column(Integer, unique=True, index=True, nullable=True)
    title = Column(String, nullable=False)
    genres = Column(String, default="")
    overview = Column(Text, default="")
    poster_path = Column(String, nullable=True)
    release_year = Column(Integer, nullable=True)

    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist_items")
    movie = relationship("Movie")
