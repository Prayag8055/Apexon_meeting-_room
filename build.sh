#!/usr/bin/env bash
# Render Build Script — runs once per deploy
set -e

echo "📦 Installing Python dependencies..."
pip install -r room-booking-api/requirements.txt

echo "📦 Installing Node dependencies & building React..."
cd react-app
npm install
npm run build
cd ..

echo "✅ Build complete"
