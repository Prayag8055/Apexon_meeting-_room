"""
Workspace-root entry point for the Room Booking API.

Run with:
    py run_api.py
"""
import sys
import os
import importlib.util

# Make the room-booking-api directory importable as a flat package
# by adding it directly to sys.path so its sub-packages (core, db, etc.)
# are importable without a top-level package prefix.
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "room-booking-api")
sys.path.insert(0, api_dir)

# Patch relative imports: rewrite them as absolute imports by loading
# the modules manually under their simple names.
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[api_dir],
    )
