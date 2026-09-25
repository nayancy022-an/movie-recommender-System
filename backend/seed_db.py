"""
Loads data/movies_sample.csv into the SQL database (Movie table).
Run once after creating the DB: python seed_db.py
"""
import pandas as pd

from app.database import SessionLocal, Base, engine
from app import models

Base.metadata.create_all(bind=engine)


def seed():
    df = pd.read_csv("data/movies_sample.csv")
    db = SessionLocal()
    try:
        added, updated = 0, 0
        for _, row in df.iterrows():
            poster = row.get("poster_path") if pd.notna(row.get("poster_path")) else None
            release_year = int(row["release_year"]) if pd.notna(row.get("release_year")) else None

            existing = db.query(models.Movie).filter(models.Movie.tmdb_id == row["tmdb_id"]).first()
            if existing:
                # keep an already-seeded row in sync with the CSV (e.g. after
                # fetch_posters.py fills in poster_path)
                existing.title = row["title"]
                existing.genres = row.get("genres", "") or ""
                existing.overview = row.get("overview", "") or ""
                existing.poster_path = poster
                existing.release_year = release_year
                updated += 1
                continue

            movie = models.Movie(
                tmdb_id=int(row["tmdb_id"]),
                title=row["title"],
                genres=row.get("genres", "") or "",
                overview=row.get("overview", "") or "",
                poster_path=poster,
                release_year=release_year,
            )
            db.add(movie)
            added += 1
        db.commit()
        print(f"Seeded {added} new movies, updated {updated} existing.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
