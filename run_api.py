"""
Workspace-root entry point for the Apexon Room Booking API.

Run with:
    python run_api.py
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Make the room-booking-api directory importable
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "room-booking-api")
sys.path.insert(0, api_dir)

import uvicorn

if __name__ == "__main__":
    print("\n🏢 Apexon Room Booking API")
    print("=" * 40)
    print(f"  Server:  http://localhost:8000")
    print(f"  Docs:    http://localhost:8000/docs")
    print(f"  Health:  http://localhost:8000/health")
    print("=" * 40 + "\n")
    uvicorn.run(
        "fastapi_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[api_dir],
    )
