# CineMatch — Full-Stack Movie Recommendation System

A complete rewrite of the original Streamlit movie recommender into a
production-style full-stack app: **React** frontend, **FastAPI** backend,
**PostgreSQL/SQLite** database, and a **Sentence-BERT + FAISS** hybrid
recommendation engine (content-based + collaborative).

## Architecture

```
[React (Vite) Frontend] <---> [FastAPI Backend] <---> [PostgreSQL / SQLite]
                                     |
                                     |---> [TMDB API]   (movie metadata, posters)
                                     |---> [FAISS Index] (Sentence-BERT embeddings)
```

- **Auth**: JWT-based signup/login (bcrypt password hashing)
- **Content-based recs**: `all-MiniLM-L6-v2` Sentence-BERT embeddings of
  title + genres + overview, indexed with FAISS (`IndexFlatIP` / cosine
  similarity)
- **Personalized ("hybrid") recs**: weighted average of embeddings for
  movies the user rated highly → nearest neighbours in the same FAISS
  index → cold-start users fall back to popularity
- **Graceful degradation**: if `sentence-transformers`/`faiss-cpu` aren't
  installed yet, the ML module automatically falls back to TF-IDF so the
  rest of the API still boots and works during development

## Project structure

```
backend/
  app/
    main.py            FastAPI app, CORS, router registration
    config.py           Settings (env vars)
    database.py          SQLAlchemy engine/session
    models.py            User, Movie, Rating, WatchlistItem
    schemas.py            Pydantic request/response models
    auth.py                 JWT + bcrypt helpers
    deps.py                  get_current_user dependency
    routers/
      auth.py                signup / login
      movies.py               search / list / detail
      recommend.py            content-based + personalized recs
      users.py                ratings + watchlist + profile
    ml/
      embeddings.py            SBERT (with TF-IDF fallback)
      build_index.py            offline script: builds the FAISS index
  data/movies_sample.csv      demo dataset (20 movies) — swap for your
                                full TMDB export
  seed_db.py                    loads movies_sample.csv into the DB
  requirements.txt
  .env.example

frontend/
  src/
    api.js               axios client (auth header injection)
    App.jsx                routes
    pages/                 Home, Search, MovieDetail, Watchlist, Login, Signup
    components/              Navbar, MovieCard, ProtectedRoute
  package.json
  .env.example
```

## Local setup

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # edit SECRET_KEY, TMDB_API_KEY etc.

python seed_db.py               # loads demo movies into the DB
python -m app.ml.build_index    # builds the FAISS index (first run downloads the SBERT model)

uvicorn app.main:app --reload   # http://localhost:8000  (docs at /docs)
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=http://localhost:8000
npm run dev                     # http://localhost:5173
```

### 3. Using your real TMDB dataset

Replace `backend/data/movies_sample.csv` with your existing TMDB export
(same columns: `tmdb_id,title,genres,overview,poster_path,release_year`),
then re-run `python seed_db.py` and `python -m app.ml.build_index`.

## Deployment

| Piece | Suggested platform |
|---|---|
| Frontend | Vercel / Netlify (`npm run build` → `dist/`) |
| Backend | Render / Railway (`uvicorn app.main:app`) |
| Database | Neon / Supabase (swap `DATABASE_URL` to Postgres) |

Update `allow_origins` in `backend/app/main.py` and
`VITE_API_BASE_URL` in the frontend `.env` once deployed.

## What was tested

The whole flow was verified end-to-end before delivery: signup → login →
JWT-protected routes → movie search → rating a movie → adding/removing a
watchlist item → building the FAISS index → content-based "similar
movies" → personalized "for you" recommendations (cold-start and
rated-user paths both checked). The React app builds cleanly with `npm
run build`.

## Resume bullet points (for your Accenture application)

- Re-architected a Streamlit movie recommender into a full-stack web app
  (**React, FastAPI, PostgreSQL**), adding JWT authentication, a ratings/
  watchlist system, and a REST API consumed by a decoupled SPA frontend.
- Built a hybrid recommendation engine combining **Sentence-BERT
  embeddings with FAISS vector search** (content-based) and a
  ratings-weighted nearest-neighbour model (personalized), with automatic
  fallback to TF-IDF for environments without ML dependencies installed.
- Designed a normalized relational schema (users, movies, ratings,
  watchlist) and RESTful endpoints for search, recommendations, and
  user-personalization features.
- Containerization-ready structure with environment-based config, CORS
  handling, and a deployment path to Vercel (frontend) + Render/Railway
  (backend) + managed Postgres.

Tweak the wording to match what you actually built/deployed — recruiters
and ATS systems both respond well to specific tech names (FastAPI, JWT,
FAISS, Sentence-BERT, React Router) so keep those explicit.
