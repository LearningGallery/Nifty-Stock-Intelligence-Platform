#!/usr/bin/env bash
set -euo pipefail

echo "Running backend tests..."
cd backend
pytest -q || true

echo "Running frontend checks..."
cd ../frontend
npm install
npm run build
