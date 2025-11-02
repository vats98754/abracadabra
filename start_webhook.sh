#!/bin/bash
set -e

echo "🚀 Starting Omi Song Recognition Webhook..."

# Install minimal webhook dependencies (uses requirements-webhook.txt instead of requirements.txt)
echo "📦 Installing webhook dependencies..."
pip install -r requirements-webhook.txt

# Install abracadabra package (skip dependencies since we installed them already)
echo "📦 Installing abracadabra package..."
pip install -e . --no-deps

# Initialize database if it doesn't exist
if [ ! -f "abracadabra.db" ]; then
    echo "🗄️  Initializing database..."
    song_recogniser initialise
    echo "✅ Database initialized"
else
    echo "✅ Database already exists"
fi

# Start the webhook server
echo "🎵 Starting webhook server on port $PORT..."
uvicorn omi_song_recognition_webhook:app --host 0.0.0.0 --port ${PORT:-8000}
