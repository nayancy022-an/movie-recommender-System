"""
Fetches poster_path for every movie in data/movies_sample.csv from TMDB,
using the tmdb_id column that's already there, and writes it back into the CSV.

Requires TMDB_API_KEY in backend/.env
(get a free key at https://www.themoviedb.org/settings/api -> "API Read Access Token"
or the v3 "API Key").

Run (from the backend/ folder, with venv activated):
    python fetch_posters.py

Then reload the DB so the app actually picks up the new posters:
    python seed_db.py
"""
import time

import pandas as pd
import requests

from app.config import settings

CSV_PATH = "data/movies_sample.csv"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{}"


def fetch_poster(tmdb_id: int) -> str | None:
    try:
        resp = requests.get(
            TMDB_MOVIE_URL.format(tmdb_id),
            params={"api_key": settings.tmdb_api_key},
            timeout=10,
        )
    except requests.RequestException as exc:
        print(f"  ! tmdb_id={tmdb_id} -> request failed: {exc}")
        return None

    if resp.status_code != 200:
        print(f"  ! tmdb_id={tmdb_id} -> HTTP {resp.status_code}")
        return None

    return resp.json().get("poster_path")


def main():
    if not settings.tmdb_api_key:
        raise SystemExit(
            "TMDB_API_KEY is not set.\n"
            "1. Create a free account at https://www.themoviedb.org\n"
            "2. Go to Settings -> API and copy the 'API Key (v3 auth)'\n"
            "3. Put it in backend/.env as TMDB_API_KEY=xxxxxxxx"
        )

    df = pd.read_csv(CSV_PATH)
    updated = 0
    for i, row in df.iterrows():
        poster = fetch_poster(int(row["tmdb_id"]))
        if poster:
            df.at[i, "poster_path"] = poster
            updated += 1
            print(f"  \u2713 {row['title']} -> {poster}")
        else:
            print(f"  \u2717 {row['title']} -> no poster found")
        time.sleep(0.25)  # go easy on TMDB's rate limit

    df.to_csv(CSV_PATH, index=False)
    print(f"\nUpdated {updated}/{len(df)} rows in {CSV_PATH}")
    print("Now run: python seed_db.py   (to reload posters into the database)")


if __name__ == "__main__":
    main()
