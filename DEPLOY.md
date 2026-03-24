# 🏢 Apexon RoomBook — Deployment Guide

## Quick Deploy (Docker)

### Prerequisites
- Docker installed on the server machine
- Port 80 available

### One-Command Deploy
```bash
docker compose up -d --build
```

App will be live at `http://<server-ip>` — share this URL with all employees.

### Default Admin Login
- Email: `admin@apexon.com`
- Password: `admin123`

---

## Deploy to Cloud (Recommended for company-wide access)

### Option 1: AWS EC2 (Most common for companies)

1. Launch an EC2 instance (t3.small is enough, Amazon Linux 2023)
2. Open port 80 in Security Group
3. SSH into the instance:
   ```bash
   sudo yum install docker git -y
   sudo systemctl start docker
   sudo usermod -aG docker ec2-user
   git clone <your-repo-url>
   cd Apexon_meeting-_room
   docker compose up -d --build
   ```
4. Access at `http://<ec2-public-ip>`
5. (Optional) Point a domain like `roombook.apexon.com` to the EC2 IP

### Option 2: Railway (Easiest, no server management)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. New Project → Deploy from GitHub repo
4. Railway auto-detects the Dockerfile
5. Add a volume mount for `/data` (for SQLite persistence)
6. Get your public URL — done

### Option 3: Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New Web Service → Connect GitHub repo
4. Set Docker as the build method
5. Add a persistent disk mounted at `/data`
6. Deploy — get your URL

### Option 4: Azure / GCP

Same Docker approach — push to Azure Container Instances or Google Cloud Run.

---

## Data Persistence

The SQLite database is stored at `/data/bookings.db` inside the container.
The `docker-compose.yml` uses a named volume (`roombook-data`) so data survives container restarts.

For production with many concurrent users, consider migrating to PostgreSQL.

---

## Custom Domain (Optional)

Once deployed, you can point a domain like `roombook.apexon.com`:
1. Add an A record pointing to your server IP
2. For HTTPS, add Cloudflare in front (free) or use Let's Encrypt with certbot
