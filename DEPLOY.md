# 🏢 Apexon RoomBook — Deployment Guide

## Deploy to Render.com (Recommended)

### Step 1: Push to GitHub

```bash
# If you haven't created a GitHub repo yet:
# 1. Go to github.com → New Repository
# 2. Name it: apexon-roombook (or any name)
# 3. Keep it Private, don't add README
# 4. Copy the repo URL

# Then push:
git remote set-url origin https://github.com/YOUR_USERNAME/apexon-roombook.git
git push -u origin dev
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **New +** → **Web Service**
3. Connect your GitHub repo (`apexon-roombook`)
4. Render auto-detects the **Dockerfile** — no config needed
5. Set these options:
   - **Name**: `apexon-roombook`
   - **Region**: Pick closest to your office
   - **Instance Type**: Free (or Starter for better performance)
   - **Branch**: `dev`
6. Under **Advanced** → **Add Disk**:
   - **Mount Path**: `/data`
   - **Size**: 1 GB (enough for SQLite)
7. Click **Deploy Web Service**

### Step 3: Done!

- Render gives you a URL like `https://apexon-roombook.onrender.com`
- Share this URL with all employees
- First deploy auto-seeds 12 rooms + admin account
- **Admin login**: `admin@apexon.com` / `admin123`

---

## Local Development

```bash
# Start API + React dev server
python serve.py
# Visit http://localhost:8000
```

## Docker (Local or Self-Hosted)

```bash
docker compose up -d --build
# Visit http://localhost
```

---

## Data Persistence

- SQLite database stored at `/data/bookings.db` in the container
- Render persistent disk keeps data across deploys
- `docker-compose.yml` uses a named volume for local Docker

## Default Admin

- Email: `admin@apexon.com`
- Password: `admin123`
- Change this after first login!
