"""
Apexon RoomBook — Production Server
Serves React frontend + FastAPI backend on a single port.
Run: python serve.py
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


def _seed_if_needed():
    """Auto-seed rooms and admin on first run (empty DB)."""
    try:
        from db.sqlite_adapter import SQLiteRoomRepo, SQLiteBookingRepo, SQLiteUserRepo
        from shared.config import get_db_path
        db = get_db_path()
        room_repo = SQLiteRoomRepo(db)
        SQLiteBookingRepo(db)
        user_repo = SQLiteUserRepo(db)

        if len(room_repo.list()) == 0:
            logging.info("🏢 First run — seeding rooms and admin...")
            from core import rooms as rooms_core, users as users_core
            ROOMS = [
                {"name": "Board Room 01", "floor": 1, "capacity": 20, "amenities": ["Projector", "Video Conferencing", "Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Board Room Side Cabin 02 (Prajyot Gandhi)", "floor": 1, "capacity": 6, "amenities": ["Projector", "Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Cabin 03 (Nitesh Palresa)", "floor": 1, "capacity": 4, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Lazy Lawn 04 (Conference Room)", "floor": 1, "capacity": 30, "amenities": ["Projector", "Video Conferencing", "Whiteboard", "Natural Light", "Air Conditioning"], "status": "active"},
                {"name": "Cabin 05 (Amay Bhide)", "floor": 1, "capacity": 4, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Jump Start Cabin 06", "floor": 1, "capacity": 8, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Front End Meeting Room 07", "floor": 1, "capacity": 12, "amenities": ["Whiteboard", "Standing Desk", "Air Conditioning"], "status": "active"},
                {"name": "Open Secret Cabin 08", "floor": 1, "capacity": 6, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Critics Court Cabin 09", "floor": 1, "capacity": 8, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Jabbers Joint Cabin 10", "floor": 1, "capacity": 10, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
                {"name": "Hearls Hault Cabin 11", "floor": 1, "capacity": 8, "amenities": ["Whiteboard", "Phone", "Air Conditioning"], "status": "active"},
                {"name": "Lab Cabin 12", "floor": 1, "capacity": 15, "amenities": ["Whiteboard", "Air Conditioning"], "status": "active"},
            ]
            for r in ROOMS:
                rooms_core.create_room(room_repo, r)
            logging.info("  ✅ 12 rooms seeded")

            try:
                users_core.register_user(user_repo, {"name": "Admin", "email": "admin@apexon.com", "password": "admin123", "department": "Operations", "role": "admin"})
                logging.info("  ✅ Admin user seeded (admin@apexon.com / admin123)")
            except Exception:
                logging.info("  ℹ️ Admin already exists")
    except Exception as e:
        logging.warning(f"Seed check skipped: {e}")


_seed_if_needed()

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
    port = int(os.environ.get("PORT", 8000))
    print()
    print("🏢 Apexon RoomBook — Production Server")
    print("=" * 45)
    print(f"  App:     http://localhost:{port}")
    print(f"  API:     http://localhost:{port}/api")
    print(f"  Docs:    http://localhost:{port}/api/docs")
    print("=" * 45)
    print()
    uvicorn.run(app, host="0.0.0.0", port=port)
