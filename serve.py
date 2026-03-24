"""
Apexon RoomBook — Production Server
Serves React frontend + FastAPI backend on a single port.
Run: python serve.py
Then tunnel with: ngrok http 8000
"""
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Make room-booking-api importable
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "room-booking-api")
sys.path.insert(0, api_dir)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi_app.main import app as api_app

# The combined app: mount API under /api, serve React for everything else
app = FastAPI(title="Apexon RoomBook")

# Mount the API routes under /api prefix
app.mount("/api", api_app)

# Serve React static build
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "react-app", "dist")

if os.path.isdir(DIST_DIR):
    # Serve static assets (JS, CSS, images)
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve other static files (favicon, etc.)
    @app.get("/vite.svg")
    async def vite_svg():
        return FileResponse(os.path.join(DIST_DIR, "vite.svg"))

    # SPA fallback — all other routes serve index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Check if it's a real file in dist
        file_path = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html (React Router handles routing)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
else:
    @app.get("/")
    async def no_build():
        return {"error": "React build not found. Run: cd react-app && npm run build"}


if __name__ == "__main__":
    import uvicorn
    print()
    print("🏢 Apexon RoomBook — Production Server")
    print("=" * 45)
    print(f"  App:     http://localhost:8000")
    print(f"  API:     http://localhost:8000/api")
    print(f"  Docs:    http://localhost:8000/api/docs")
    print()
    print("  To share with your company, run:")
    print("    ngrok http 8000")
    print("  Then share the ngrok URL with everyone.")
    print("=" * 45)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
