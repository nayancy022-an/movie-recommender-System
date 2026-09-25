#!/usr/bin/env bash
# Single build script for Railway: builds the React frontend and copies
# the output into backend/static so FastAPI can serve it directly.
set -e

echo "==> Building frontend"
cd frontend
npm install
npm run build
cd ..

echo "==> Copying frontend build into backend/static"
rm -rf backend/static
cp -r frontend/dist backend/static

echo "==> Installing backend dependencies"
cd backend
pip install -r requirements.txt

echo "==> Seeding DB + building recommendation index"
python seed_db.py
python -m app.ml.build_index

echo "Build complete."
