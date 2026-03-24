"""
Apexon RoomBook — Tunnel Script
Creates a public URL for your local server so anyone can access it.

Prerequisites: python serve.py must be running on port 8000

Usage:
  python tunnel.py              (uses ngrok — needs free signup at ngrok.com)
  python tunnel.py --token YOUR_NGROK_TOKEN   (first time setup)
"""
import sys
import os
import time

def main():
    token = None
    for i, arg in enumerate(sys.argv):
        if arg == '--token' and i + 1 < len(sys.argv):
            token = sys.argv[i + 1]

    try:
        from pyngrok import ngrok, conf

        # Set auth token if provided
        if token:
            ngrok.set_auth_token(token)
            print(f"✅ Auth token saved. You won't need to provide it again.\n")

        print("🏢 Apexon RoomBook — Creating Public Tunnel")
        print("=" * 50)
        print("⏳ Starting tunnel to localhost:8000...")
        print()

        # Open tunnel
        tunnel = ngrok.connect(8000, "http")
        public_url = tunnel.public_url

        print(f"  ✅ TUNNEL IS LIVE!")
        print()
        print(f"  🌐 Public URL:  {public_url}")
        print()
        print(f"  Share this URL with your team:")
        print(f"  ┌─────────────────────────────────────────┐")
        print(f"  │  {public_url:<40}│")
        print(f"  └─────────────────────────────────────────┘")
        print()
        print(f"  Admin Login:")
        print(f"    Email:    admin@apexon.com")
        print(f"    Password: admin123")
        print()
        print(f"  Press Ctrl+C to stop the tunnel.")
        print("=" * 50)

        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Tunnel stopped.")
            ngrok.disconnect(tunnel.public_url)

    except Exception as e:
        error_msg = str(e)
        if 'ERR_NGROK_105' in error_msg or 'auth' in error_msg.lower():
            print("❌ ngrok requires a free auth token.")
            print()
            print("  Quick setup (takes 30 seconds):")
            print("  1. Go to https://dashboard.ngrok.com/signup")
            print("  2. Sign up (free)")
            print("  3. Copy your auth token from the dashboard")
            print("  4. Run: python tunnel.py --token YOUR_TOKEN")
            print()
        else:
            print(f"❌ Error: {e}")
            print()
            print("  Alternative: Use SSH tunnel (no signup needed):")
            print("    ssh -R 80:localhost:8000 serveo.net")
            print()


if __name__ == '__main__':
    main()
