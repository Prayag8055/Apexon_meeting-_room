import sqlite3
import csv
import uuid
import json
from datetime import datetime

DB_FILE = "bookings.db"
CSV_FILE = "location_wise_rooms_cleaned.csv"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

now = datetime.now().isoformat()
inserted = 0

def clean(v):
    return v.strip() if v and v.strip() != "" else None

def yes_no(v):
    return 1 if v and v.strip().lower() == "yes" else 0

print("📥 Importing CSV...")

with open(CSV_FILE, encoding="cp1252", errors="ignore") as f:
    reader = csv.DictReader(f)

    for row in reader:
        try:
            name = clean(row.get("Room Name"))
            location = clean(row.get("Location / Building"))
            floor = clean(row.get("Floor"))
            room_type = clean(row.get("Room Type"))
            cabin_type = clean(row.get("Cabin Type"))

            capacity = clean(row.get("Seating Capacity"))
            capacity = int(capacity) if capacity and capacity.isdigit() else 0

            amenities_raw = clean(
                row.get("Amenities Available (Projector, Whiteboard, TV,")
            )

            # Convert amenities to JSON list
            if amenities_raw and amenities_raw.lower() != "no":
                amenities = json.dumps(
                    [a.strip() for a in amenities_raw.split(",")]
                )
            else:
                amenities = "[]"

            vc_enabled = yes_no(row.get("VC Enabled"))
            power_points = yes_no(row.get("Power Points"))

            room_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO location_wise_rooms (
                    room_id,
                    name,
                    location,
                    floor,
                    room_type,
                    cabin_type,
                    capacity,
                    amenities,
                    vc_enabled,
                    power_points,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                room_id,
                name,
                location,
                floor,
                room_type,
                cabin_type,
                capacity,
                amenities,
                vc_enabled,
                power_points,
                "active",
                now,
                now
            ))

            inserted += 1

        except Exception as e:
            print("❌ Error in row:", row)
            print(e)

conn.commit()
conn.close()

print(f"🎉 Done! Inserted {inserted} rows successfully.")
