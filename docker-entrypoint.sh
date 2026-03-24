#!/bin/bash
set -e

echo "🏢 Apexon RoomBook — Starting..."
echo "================================="

# Render sets PORT env var; default to 80 for local Docker
export PORT=${PORT:-80}
echo "  Listening on port: $PORT"

# Substitute PORT into nginx config
envsubst '$PORT' < /etc/nginx/conf.d/default.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/conf.d/default.conf

# Set Python path
export PYTHONPATH=/app/room-booking-api

# Initialize database
echo "📦 Initializing database..."
python -c "
import sys
sys.path.insert(0, '/app/room-booking-api')
from db.sqlite_adapter import SQLiteRoomRepo, SQLiteBookingRepo, SQLiteUserRepo
db = '/data/bookings.db'
SQLiteRoomRepo(db)
SQLiteBookingRepo(db)
SQLiteUserRepo(db)
print('  ✅ Database ready')
"

# Seed rooms if empty
echo "🏢 Checking rooms..."
python -c "
import sys, os
sys.path.insert(0, '/app/room-booking-api')
os.environ['DB_PATH'] = '/data/bookings.db'
from db.sqlite_adapter import SQLiteRoomRepo
repo = SQLiteRoomRepo('/data/bookings.db')
rooms = repo.list()
if len(rooms) == 0:
    print('  Seeding rooms...')
    import subprocess, time, requests
    proc = subprocess.Popen(
        ['python', '-m', 'uvicorn', 'fastapi_app.main:app', '--host', '0.0.0.0', '--port', '8000'],
        cwd='/app/room-booking-api',
        env={**os.environ, 'DB_PATH': '/data/bookings.db', 'PYTHONPATH': '/app/room-booking-api'},
    )
    time.sleep(3)
    try:
        exec(open('/app/seed_rooms.py').read())
        exec(open('/app/seed_admin.py').read())
    except Exception as e:
        print(f'  ⚠️ Seed error: {e}')
    proc.terminate()
    proc.wait()
else:
    print(f'  ✅ {len(rooms)} rooms already exist')
"

echo ""
echo "🚀 Starting services..."
echo "  Frontend: http://0.0.0.0:$PORT"
echo "  API:      http://0.0.0.0:8000"
echo "================================="
echo ""

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
