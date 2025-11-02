#!/usr/bin/env bash
# Render build script

set -o errexit

echo "🚀 Building Omi Song Recognition Webhook for Render..."

# Install minimal webhook dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-webhook.txt

# Install abracadabra package (without dependencies to avoid PyAudio)
echo "📦 Installing abracadabra package..."
pip install -e . --no-deps

# Initialize database
echo "🗄️  Initializing database..."
song_recogniser initialise || echo "⚠️  Database initialization will happen at runtime"

echo "✅ Build complete!"
