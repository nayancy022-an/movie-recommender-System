import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.routers import auth, movies, recommend, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Recommender API",
    description="Full-stack movie recommendation system — FastAPI + FAISS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # single-origin deploy (frontend served by this same app) — tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(recommend.router)
app.include_router(users.router)

# Serve the built React app (frontend/dist) from this same FastAPI process,
# so ONE Railway service handles both API + frontend — no separate Vercel
# deploy, no CORS headaches, no second URL to manage.
_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.isdir(_FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Any path not matched by the API routers above falls through here.
        # React Router handles client-side routing, so always return index.html.
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def health_check():
        return {"status": "ok", "service": "movie-recommender-api", "note": "frontend not built yet"}
