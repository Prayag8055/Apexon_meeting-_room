"""Seed script — creates all rooms via the Room Booking API."""
import requests
import csv
import json


BASE_URL = "http://localhost:8000"

# Rules:
# - No floor field (all same floor)
# - AC is everywhere
# - Only Front End Meeting Room 07 has Standing Desk
# - Board Room 01, Board Room Side Cabin 02, Lazy Lawn 04 have Projector
# - Lazy Lawn 04 has Natural Light
# - Board rooms + Lazy Lawn have Video Conferencing + Whiteboard
# - Other rooms get Whiteboard + Phone as appropriate

def load_rooms_from_csv(file_path):
    rooms = []

    def clean(v):
        return v.strip() if v and v.strip() != "" else None

    # ✅ ADD IT HERE
    def yes_no(v):
        return True if v and v.strip().lower() == "yes" else False

    with open(file_path, encoding="cp1252", errors="ignore") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                amenities_raw = clean(
                    row.get("Amenities Available (Projector, Whiteboard, TV,")
                )

                if amenities_raw and amenities_raw.lower() != "no":
                    amenities = [a.strip() for a in amenities_raw.split(",")]
                else:
                    amenities = []

                capacity = clean(row.get("Seating Capacity"))
                capacity = int(capacity) if capacity and capacity.isdigit() else 0

                # ✅ USE IT HERE
                room = {
                    "name": clean(row.get("Room Name")),
                    "location": clean(row.get("Location / Building")) or "Default",
                    "floor": int(clean(row.get("Floor")) or 1),
                    "capacity": capacity,
                    "amenities": amenities,
                    "status": "active",

                    "room_type": clean(row.get("Room Type")),
                    "cabin_type": clean(row.get("Cabin Type")),
                    "vc_enabled": yes_no(row.get("VC Enabled")),
                    "power_points": yes_no(row.get("Power Points")),
                }

                rooms.append(room)

            except Exception as e:
                print("❌ Error parsing row:", e)

    return rooms


CSV_FILE = "location_wise_rooms_cleaned.csv"
ROOMS = load_rooms_from_csv(CSV_FILE)

def main():
    print("\n🏢 Apexon Room Booking — Room Seeder")
    print("=" * 40)
    print(f"Connecting to {BASE_URL}...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        r.raise_for_status()
        print("✅ API is up\n")
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        print("   Make sure to run: python run_api.py")
        return

    created = 0
    for room in ROOMS:
        try:
            resp = requests.post(f"{BASE_URL}/rooms", json=room, timeout=5)
            if resp.status_code == 201:
                data = resp.json()
                print(f"  ✅ Created: {data['name']}  (id: {data['room_id'][:8]}…)")
                created += 1
            
            elif resp.status_code == 400 and "already exists" in resp.text.lower():
                print(f"⏩ Skipped (duplicate): {room['name']}")

            else:
                print(f"  ⚠️  {room['name']} — {resp.status_code}: {resp.text[:80]}")
        except Exception as e:
            print(f"  ❌ {room['name']} — {e}")

    print(f"\n{created}/{len(ROOMS)} rooms created.")


if __name__ == "__main__":
    main()
