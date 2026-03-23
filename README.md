# 🏢 Apexon Room Booking System

A production-grade meeting room booking application for Apexon employees.

## Quick Start

### 1. Install dependencies

```bash
pip install -r room-booking-api/requirements.txt
pip install -r streamlit_app/requirements.txt
```

### 2. Start the API server

```bash
python run_api.py
```

API runs at http://localhost:8000 (Swagger docs at /docs)

### 3. Seed rooms (first time only)

```bash
python seed_rooms.py
```

### 4. Start the UI

```bash
cd streamlit_app
streamlit run app.py
```

UI runs at http://localhost:8501

## Features

- **Dashboard** — KPIs, quick booking, upcoming meetings timeline
- **Room Management** — Create, edit, deactivate rooms with amenities
- **Booking System** — Book, reschedule, cancel with conflict detection
- **User Management** — Register team members, view booking history
- **Availability Viewer** — Visual 30-min slot grid per room per day
- **Search & Filters** — Filter by room, user, date, status, capacity

## Architecture

- **Backend**: FastAPI + SQLite (room-booking-api/)
- **Frontend**: Streamlit with custom dark theme (streamlit_app/)
- **Business hours**: 08:00–20:00 (configurable via env vars)
