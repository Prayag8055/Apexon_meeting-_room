"""Seed script — creates all 12 rooms via the Room Booking API."""
import requests

BASE_URL = "http://localhost:8000"

# Rules:
# - No floor field (all same floor)
# - AC is everywhere
# - Only Front End Meeting Room 07 has Standing Desk
# - Board Room 01, Board Room Side Cabin 02, Lazy Lawn 04 have Projector
# - Lazy Lawn 04 has Natural Light
# - Board rooms + Lazy Lawn have Video Conferencing + Whiteboard
# - Other rooms get Whiteboard + Phone as appropriate

ROOMS = [
    {
        "name": "Board Room 01",
        "floor": 1,
        "capacity": 20,
        "amenities": ["Projector", "Video Conferencing", "Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Board Room Side Cabin 02 (Prajyot Gandhi)",
        "floor": 1,
        "capacity": 6,
        "amenities": ["Projector", "Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Cabin 03 (Nitesh Palresa)",
        "floor": 1,
        "capacity": 4,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Lazy Lawn 04 (Conference Room)",
        "floor": 1,
        "capacity": 30,
        "amenities": ["Projector", "Video Conferencing", "Whiteboard", "Natural Light", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Cabin 05 (Amay Bhide)",
        "floor": 1,
        "capacity": 4,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Jump Start Cabin 06",
        "floor": 1,
        "capacity": 8,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Front End Meeting Room 07",
        "floor": 1,
        "capacity": 12,
        "amenities": ["Whiteboard", "Standing Desk", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Open Secret Cabin 08",
        "floor": 1,
        "capacity": 6,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Critics Court Cabin 09",
        "floor": 1,
        "capacity": 8,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Jabbers Joint Cabin 10",
        "floor": 1,
        "capacity": 10,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Hearls Hault Cabin 11",
        "floor": 1,
        "capacity": 8,
        "amenities": ["Whiteboard", "Phone", "Air Conditioning"],
        "status": "active",
    },
    {
        "name": "Lab Cabin 12",
        "floor": 1,
        "capacity": 15,
        "amenities": ["Whiteboard", "Air Conditioning"],
        "status": "active",
    },
]


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
            else:
                print(f"  ⚠️  {room['name']} — {resp.status_code}: {resp.text[:80]}")
        except Exception as e:
            print(f"  ❌ {room['name']} — {e}")

    print(f"\n{created}/{len(ROOMS)} rooms created.")


if __name__ == "__main__":
    main()
