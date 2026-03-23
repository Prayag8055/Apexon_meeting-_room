"""Seed script — creates the default admin user."""
import requests

BASE_URL = "http://localhost:8000"

ADMIN = {
    "name": "Admin",
    "email": "admin@apexon.com",
    "password": "admin123",
    "department": "Operations",
    "role": "admin",
}


def main():
    print("\n🛡️  Apexon Room Booking — Admin Seeder")
    print("=" * 40)
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        r.raise_for_status()
        print("✅ API is up\n")
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        print("   Run: python run_api.py")
        return

    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=ADMIN, timeout=5)
        if resp.status_code == 201:
            data = resp.json()
            print(f"  ✅ Admin created: {data['name']} ({data['email']})")
            print(f"     Role: {data['role']}")
            print(f"\n  Login with:")
            print(f"    Email:    admin@apexon.com")
            print(f"    Password: admin123")
        elif resp.status_code == 409:
            print("  ℹ️  Admin already exists.")
        else:
            print(f"  ⚠️  {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"  ❌ {e}")

    print()


if __name__ == "__main__":
    main()
