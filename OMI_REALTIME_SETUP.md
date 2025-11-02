# Omi Real-Time Audio Streaming Setup for Song Recognition

## Overview

This guide shows you how to set up song recognition using Omi's **Real-Time Audio Streaming** feature. The Omi device will stream raw audio bytes to your webhook, and your server will recognize songs and notify users.

## Architecture

```
┌─────────────────────┐
│  Omi Wearable       │  User listens to music
│  DevKit1/DevKit2    │
└──────────┬──────────┘
           │ Streams raw audio bytes
           │ (every X seconds)
           ▼
┌─────────────────────────────────────────────────┐
│  Omi Backend                                    │
│  POST /audio?sample_rate=16000&uid=user123     │
│  Content-Type: application/octet-stream         │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│  YOUR WEBHOOK SERVER                             │
│  (omi_song_recognition_webhook.py)              │
│                                                  │
│  1. Receive raw audio bytes                     │
│  2. Add WAV header → create audio file          │
│  3. Run: song_recogniser.recognise()            │
│  4. Parse result                                │
│  5. Send notification (via Omi notification API)│
└──────────┬───────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  User's Omi App     │
│  📱 NOTIFICATION:   │  "🎵 Despacito by Luis Fonsi"
└─────────────────────┘
```

## How Real-Time Audio Streaming Works

### Audio Format
- **Content-Type**: `application/octet-stream` (raw bytes)
- **Sample Rate**:
  - 16,000 Hz (DevKit1 v1.0.4+ and DevKit2)
  - 8,000 Hz (DevKit1 v1.0.2)
- **Bit Depth**: 16-bit (2 bytes per sample)
- **Channels**: Mono (1 channel)

### Request Format
```
POST /audio?sample_rate=16000&uid=user123
Content-Type: application/octet-stream

[Raw audio bytes]
```

### Frequency
You configure how often audio is sent (e.g., every 10 seconds) in the Omi app settings.

## Implementation

### Step 1: Install Dependencies

```bash
cd /Users/anvayvats/abracadabra

# Install FastAPI and uvicorn
pip install fastapi uvicorn

# Ensure abracadabra is installed
pip install -e .
```

### Step 2: Set Up the Webhook Server

The webhook server is already created at `omi_song_recognition_webhook.py`. It:

1. **Receives audio bytes** from Omi backend
2. **Accumulates bytes** into a buffer (minimum 10 seconds)
3. **Converts to WAV format** by adding proper headers
4. **Runs song recognition** using abracadabra
5. **Sends results** to the user

### Step 3: Run the Server Locally (for testing)

```bash
# Option 1: Run directly
python omi_song_recognition_webhook.py

# Option 2: Run with uvicorn
uvicorn omi_song_recognition_webhook:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at `http://localhost:8000`

### Step 4: Expose Locally with Ngrok (for testing)

Since Omi needs a public HTTPS URL, use ngrok:

```bash
# Install ngrok if you don't have it
brew install ngrok

# Start ngrok tunnel
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok.io`

Your webhook endpoint will be: `https://abc123.ngrok.io/audio`

### Step 5: Configure in Omi App

1. Open **Omi App** on your phone
2. Go to **Settings** → **Developer Mode**
3. Scroll to **Realtime audio bytes**
4. Set your endpoint: `https://abc123.ngrok.io/audio`
5. Set **Every x seconds**: `10` (audio will be sent every 10 seconds)
6. Save settings

### Step 6: Test the Integration

1. **Wear your Omi device**
2. **Play music** (e.g., from Spotify, YouTube, etc.)
3. **Wait 10-20 seconds** (for enough audio to accumulate)
4. **Check your server logs** to see recognition happening
5. **User receives notification** (if implemented via Omi notification API)

## Server Logs Example

```
INFO: Received 320000 bytes from user user123 at 16000 Hz
INFO: User user123 buffer: 10.00 seconds of audio
INFO: Created WAV file: /tmp/omi_audio_user123_20250102_143022.wav
INFO: Attempting song recognition for user user123...
INFO: Recognition output: ('Luis Fonsi', 'Unknown', 'Despacito')
INFO: Song recognized for user user123: {'artist': 'Luis Fonsi', 'title': 'Despacito', 'confidence': 0.9}
INFO: Notification for user user123: 🎵 You're listening to: 'Despacito' by Luis Fonsi
```

## API Endpoints

### POST /audio
Main webhook endpoint for receiving audio bytes.

**Query Parameters:**
- `sample_rate` (int): Audio sample rate in Hz
- `uid` (string): User ID

**Request Body:** Raw audio bytes (application/octet-stream)

**Response:**
```json
{
  "status": "ok",
  "received_bytes": 320000
}
```

### GET /audio
Setup verification endpoint.

**Response:**
```json
{
  "is_setup_completed": true
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Omi Song Recognition",
  "active_users": 3
}
```

### GET /stats/{uid}
Get statistics for a user's audio buffer.

**Response:**
```json
{
  "uid": "user123",
  "buffer_size_bytes": 640000,
  "buffer_duration_seconds": 20.0,
  "sample_rate": 16000,
  "last_recognition": {
    "artist": "Luis Fonsi",
    "title": "Despacito",
    "confidence": 0.9
  }
}
```

### DELETE /buffer/{uid}
Clear audio buffer for a specific user.

## Deployment for Production

### Option 1: Railway

1. Create account at [railway.app](https://railway.app)
2. Create new project
3. Connect GitHub repository
4. Set environment variables (if needed)
5. Deploy
6. Get public URL: `https://your-app.railway.app`
7. Configure in Omi app: `https://your-app.railway.app/audio`

### Option 2: Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create omi-song-recognition

# Deploy
git push heroku master

# Get URL
heroku info
```

### Option 3: DigitalOcean App Platform

1. Create DigitalOcean account
2. Go to App Platform
3. Create new app from GitHub
4. Configure build settings
5. Deploy

### Option 4: Google Cloud Run

```bash
# Build container
docker build -t gcr.io/YOUR_PROJECT/omi-song-recognition .

# Push to GCR
docker push gcr.io/YOUR_PROJECT/omi-song-recognition

# Deploy to Cloud Run
gcloud run deploy omi-song-recognition \
  --image gcr.io/YOUR_PROJECT/omi-song-recognition \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Dockerfile for Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir fastapi uvicorn

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "omi_song_recognition_webhook:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Configuration Options

### Minimum Audio Length
Adjust the minimum audio required for recognition:

```python
MIN_AUDIO_LENGTH = 10  # seconds
```

Lower values = faster recognition but less accurate
Higher values = better accuracy but slower response

### Audio Buffer Management

The webhook automatically:
- **Accumulates audio** until minimum length is reached
- **Limits buffer size** to prevent memory issues (max 60 seconds)
- **Clears buffer** after successful recognition
- **Keeps recent audio** if recognition fails (for retry)

## Troubleshooting

### No Audio Received
- Check ngrok/deployment URL is correct
- Verify endpoint is set in Omi app: Settings → Developer Mode
- Check server logs for incoming requests
- Test with: `curl -X POST http://localhost:8000/health`

### Recognition Not Working
- Check if audio file is created: `/tmp/omi_audio_*.wav`
- Verify abracadabra database has songs registered
- Test song_recogniser manually: `song_recogniser recognise test.wav`
- Check detailed_recognition.py output for scores

### Memory Issues
- Reduce MAX_BUFFER_DURATION
- Clear buffers periodically: `DELETE /buffer/{uid}`
- Implement automatic buffer cleanup after inactivity

### Low Recognition Accuracy
- Increase MIN_AUDIO_LENGTH (try 15-20 seconds)
- Ensure high-quality audio registration
- Check sample rate matches device (16000 vs 8000 Hz)
- Verify music is loud enough for device to capture

## Performance Optimization

### 1. Async Recognition
Process recognition in background to avoid blocking:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def recognize_song_async(audio_file):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        recognize_song,
        audio_file
    )
```

### 2. Caching Results
Cache recent recognitions to avoid duplicate processing:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_recognition(audio_hash):
    # Recognition logic
    pass
```

### 3. Rate Limiting
Prevent excessive recognition attempts:

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/audio", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def audio_webhook(...):
    pass
```

## Sending Notifications to Users

### Important Note
The current implementation logs notifications but doesn't send them to users through Omi's interface. You have two options:

### Option 1: Use Omi Notification Integration
If Omi provides a notification API (check latest docs), implement:

```python
import httpx

async def send_omi_notification(uid: str, message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.omi.me/notifications",
            headers={"Authorization": f"Bearer {OMI_API_KEY}"},
            json={
                "uid": uid,
                "message": message,
                "type": "song_recognition"
            }
        )
        return response.status_code == 200
```

### Option 2: Create Integration App
Create a separate Omi Integration App that:
1. Receives webhook from your song recognition server
2. Uses Omi's notification system to alert users
3. Displays in user's chat interface

## Monitoring & Analytics

### Log Recognized Songs
```python
import json
from datetime import datetime

def log_recognition(uid, song_info):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "uid": uid,
        "song": song_info
    }

    with open("recognition_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### Track Metrics
- Recognition success rate
- Average recognition time
- Most recognized songs
- Active users per day

## Next Steps

1. ✅ Deploy webhook server to production
2. ⏳ Configure Omi app with production URL
3. ⏳ Test with real music playback
4. ⏳ Implement Omi notification integration
5. ⏳ Add song history/analytics dashboard
6. ⏳ Optimize recognition accuracy
7. ⏳ Scale infrastructure as needed

## Resources

- **Omi Docs**: https://docs.omi.me
- **Audio Streaming Example**: https://github.com/mdmohsin7/omi-audio-streaming
- **Abracadabra Docs**: https://abracadabra.readthedocs.io
- **FastAPI Docs**: https://fastapi.tiangolo.com

## Support

For issues or questions:
- Check server logs: `/var/log/omi-webhook.log`
- Test endpoints: `GET /health`, `GET /stats/{uid}`
- Monitor Omi app Developer Mode logs
- Review ngrok request inspector: `http://127.0.0.1:4040`
