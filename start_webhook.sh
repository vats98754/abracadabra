#!/bin/bash
set -e

echo "🚀 Starting Omi Song Recognition Webhook..."

# Install abracadabra package
echo "📦 Installing abracadabra package..."
pip install -e .

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
