#!/usr/bin/env python3
"""
Omi Song Recognition Webhook
Receives real-time audio bytes from Omi wearable and recognizes songs
"""

from fastapi import FastAPI, Request, Query, Header, UploadFile, File, Form
from fastapi.responses import JSONResponse
import subprocess
import tempfile
import os
import struct
import wave
from datetime import datetime
from pathlib import Path
import logging
import httpx
import requests
from typing import Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Omi Song Recognition Service")

# Omi App Credentials
OMI_APP_ID = os.getenv("OMI_APP_ID")
OMI_API_KEY = os.getenv("OMI_API_KEY")
OMI_API_BASE_URL = "https://api.omi.me/v1"  # Update if different

# Store audio buffers per user session
audio_buffers = {}

# Minimum audio length for recognition (seconds)
MIN_AUDIO_LENGTH = int(os.getenv("MIN_AUDIO_LENGTH", "10"))

# Maximum buffer duration before trimming (seconds)
MAX_BUFFER_DURATION = int(os.getenv("MAX_BUFFER_DURATION", "60"))

# Path to abracadabra installation
ABRACADABRA_PATH = os.getenv("ABRACADABRA_PATH", "/Users/anvayvats/abracadabra")

# Validate credentials on startup
if not OMI_APP_ID or not OMI_API_KEY:
    logger.warning("⚠️  OMI_APP_ID and OMI_API_KEY not set. Notifications will not be sent.")
    logger.warning("   Set these in .env file or environment variables.")
else:
    logger.info(f"✅ Omi app configured with ID: {OMI_APP_ID}")


def create_wav_file(audio_bytes: bytes, sample_rate: int, output_path: str):
    """
    Convert raw audio bytes to WAV file format.

    Args:
        audio_bytes: Raw PCM audio data
        sample_rate: Sample rate in Hz (16000 for DevKit1 v1.0.4+/DevKit2, 8000 for v1.0.2)
        output_path: Path to save the WAV file
    """
    num_channels = 1  # Mono audio
    sample_width = 2  # 16-bit audio (2 bytes per sample)

    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)

    logger.info(f"Created WAV file: {output_path} ({len(audio_bytes)} bytes, {sample_rate} Hz)")


def recognize_song(audio_file: str) -> dict:
    """
    Use abracadabra to recognize the song.

    Args:
        audio_file: Path to audio file

    Returns:
        dict with keys: artist, album, title, confidence, score
    """
    try:
        # Run song_recogniser command
        cmd = ['song_recogniser', 'recognise', audio_file]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=ABRACADABRA_PATH,
            timeout=30
        )

        if result.returncode != 0:
            logger.error(f"Recognition failed: {result.stderr}")
            return None

        # Parse output: ('artist', 'album', 'title')
        output = result.stdout.strip()
        logger.info(f"Recognition output: {output}")

        # Parse the tuple format
        import ast
        artist, album, title = ast.literal_eval(output)

        # Get detailed scores using detailed_recognition.py
        cmd_detailed = [
            'python',
            f'{ABRACADABRA_PATH}/detailed_recognition.py',
            audio_file
        ]
        result_detailed = subprocess.run(
            cmd_detailed,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Extract score from output
        score = parse_score_from_output(result_detailed.stdout)
        confidence = calculate_confidence(score)

        return {
            'artist': artist if artist != 'Unknown' else None,
            'album': album if album != 'Unknown' else None,
            'title': title if title != 'Unknown' else None,
            'confidence': confidence,
            'score': score,
            'recognized': confidence > 0.5
        }

    except subprocess.TimeoutExpired:
        logger.error("Recognition timeout")
        return None
    except Exception as e:
        logger.error(f"Error recognizing song: {e}")
        return None


def parse_score_from_output(output: str) -> int:
    """
    Parse confidence score from detailed_recognition.py output.
    """
    import re

    # Look for "Score: XXXX" pattern
    score_match = re.search(r'Score:\s*(\d+)', output)
    if score_match:
        return int(score_match.group(1))

    return 0


def calculate_confidence(score: int) -> float:
    """
    Convert raw score to confidence percentage (0.0 to 1.0).

    Score interpretation:
    - >1000: Very high confidence (100%)
    - 100-1000: High confidence (90%)
    - 50-100: Medium confidence (70%)
    - 10-50: Low confidence (40%)
    - <10: Very low/noise (10%)
    """
    if score > 1000:
        return 1.0
    elif score > 100:
        return 0.9
    elif score > 50:
        return 0.7
    elif score > 10:
        return 0.4
    else:
        return 0.1


def send_notification_to_user(uid: str, song_info: dict) -> bool:
    """
    Send song recognition result to user via Omi notification API.

    Uses the official Omi API endpoint format:
    POST https://api.omi.me/v2/integrations/{app_id}/notification

    Based on official examples:
    https://github.com/BasedHardware/omi/blob/main/plugins/example/notifications/hey_omi.py
    """
    if not OMI_APP_ID or not OMI_API_KEY:
        logger.warning(f"Cannot send notification to {uid}: credentials not configured")
        return False

    message = format_notification_message(song_info)
    logger.info(f"Sending notification to user {uid}: {message}")

    try:
        # Official Omi notification endpoint
        url = f"https://api.omi.me/v2/integrations/{OMI_APP_ID}/notification"

        headers = {
            "Authorization": f"Bearer {OMI_API_KEY}",
            "Content-Type": "application/json"
        }

        params = {
            "uid": uid,
            "message": message
        }

        response = requests.post(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        logger.info(f"✅ Notification sent successfully to {uid}")
        return True

    except requests.exceptions.Timeout:
        logger.error(f"❌ Notification timeout for user {uid}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error sending notification to {uid}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error sending notification to {uid}: {str(e)}")
        return False


def format_notification_message(song_info: dict) -> str:
    """
    Format song information into a user-friendly notification message.
    """
    artist = song_info.get('artist', 'Unknown Artist')
    title = song_info.get('title', 'Unknown Song')
    confidence = song_info.get('confidence', 0)

    if confidence > 0.8:
        emoji = "🎵"
        certainty = ""
    elif confidence > 0.5:
        emoji = "🎶"
        certainty = " (likely)"
    else:
        emoji = "🎼"
        certainty = " (maybe)"

    return f"{emoji} You're listening to: '{title}' by {artist}{certainty}"


@app.post("/audio")
async def audio_webhook(
    request: Request,
    sample_rate: int = Query(..., description="Audio sample rate in Hz"),
    uid: str = Query(..., description="User ID")
):
    """
    Receive real-time audio bytes from Omi device.

    This endpoint is called by Omi backend with:
    - Raw audio bytes (octet-stream) in request body
    - sample_rate: 16000 (DevKit1 v1.0.4+/DevKit2) or 8000 (DevKit1 v1.0.2)
    - uid: User's unique identifier

    The audio bytes are accumulated and processed for song recognition.
    """
    try:
        # Read raw audio bytes from request body
        audio_bytes = await request.body()

        logger.info(f"Received {len(audio_bytes)} bytes from user {uid} at {sample_rate} Hz")

        # Initialize or append to user's audio buffer
        if uid not in audio_buffers:
            audio_buffers[uid] = {
                'bytes': bytearray(),
                'sample_rate': sample_rate,
                'last_recognition': None
            }

        # Append new bytes to buffer
        audio_buffers[uid]['bytes'].extend(audio_bytes)
        audio_buffers[uid]['sample_rate'] = sample_rate

        # Calculate current audio duration in seconds
        bytes_per_sample = 2  # 16-bit audio = 2 bytes
        total_samples = len(audio_buffers[uid]['bytes']) / bytes_per_sample
        duration = total_samples / sample_rate

        logger.info(f"User {uid} buffer: {duration:.2f} seconds of audio")

        # Only attempt recognition if we have enough audio
        if duration >= MIN_AUDIO_LENGTH:
            # Create temporary WAV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.gettempdir()
            wav_filename = os.path.join(temp_dir, f"omi_audio_{uid}_{timestamp}.wav")

            try:
                # Convert raw bytes to WAV
                create_wav_file(
                    bytes(audio_buffers[uid]['bytes']),
                    sample_rate,
                    wav_filename
                )

                # Recognize song
                logger.info(f"Attempting song recognition for user {uid}...")
                song_info = recognize_song(wav_filename)

                if song_info and song_info['recognized']:
                    logger.info(f"Song recognized for user {uid}: {song_info}")

                    # Send notification to user
                    notification_sent = send_notification_to_user(uid, song_info)

                    if notification_sent:
                        logger.info(f"✅ User {uid} notified about: {song_info['title']}")
                    else:
                        logger.warning(f"⚠️  Could not notify user {uid}")

                    # Store last recognition to avoid duplicates
                    audio_buffers[uid]['last_recognition'] = song_info

                    # Clear buffer after successful recognition
                    audio_buffers[uid]['bytes'] = bytearray()
                else:
                    logger.info(f"No song recognized for user {uid} (score too low)")

                    # Keep accumulating audio for better recognition
                    # But limit buffer size to prevent memory issues
                    max_duration = 60  # seconds
                    if duration > max_duration:
                        # Keep only the last 30 seconds
                        samples_to_keep = int(30 * sample_rate * bytes_per_sample)
                        audio_buffers[uid]['bytes'] = audio_buffers[uid]['bytes'][-samples_to_keep:]
                        logger.info(f"Trimmed buffer for user {uid} to 30 seconds")

            finally:
                # Clean up temporary file
                if os.path.exists(wav_filename):
                    os.unlink(wav_filename)
                    logger.info(f"Cleaned up temp file: {wav_filename}")

        # Return success response
        return JSONResponse(
            content={"status": "ok", "received_bytes": len(audio_bytes)},
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing audio for user {uid}: {e}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


@app.get("/audio")
async def audio_setup():
    """
    Optional setup endpoint to verify webhook is configured.
    """
    return JSONResponse(
        content={"is_setup_completed": True},
        status_code=200
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "Omi Song Recognition",
            "active_users": len(audio_buffers)
        },
        status_code=200
    )


@app.get("/stats/{uid}")
async def get_user_stats(uid: str):
    """
    Get statistics for a specific user's audio buffer.
    """
    if uid not in audio_buffers:
        return JSONResponse(
            content={"error": "User not found"},
            status_code=404
        )

    buffer_info = audio_buffers[uid]
    bytes_per_sample = 2
    total_samples = len(buffer_info['bytes']) / bytes_per_sample
    duration = total_samples / buffer_info['sample_rate']

    return JSONResponse(
        content={
            "uid": uid,
            "buffer_size_bytes": len(buffer_info['bytes']),
            "buffer_duration_seconds": duration,
            "sample_rate": buffer_info['sample_rate'],
            "last_recognition": buffer_info.get('last_recognition')
        },
        status_code=200
    )


@app.delete("/buffer/{uid}")
async def clear_buffer(uid: str):
    """
    Clear audio buffer for a specific user.
    """
    if uid in audio_buffers:
        del audio_buffers[uid]
        return JSONResponse(
            content={"status": "ok", "message": f"Buffer cleared for user {uid}"},
            status_code=200
        )
    else:
        return JSONResponse(
            content={"error": "User not found"},
            status_code=404
        )


@app.post("/register")
async def register_song(
    file: UploadFile = File(...),
    artist: str = Form(None),
    title: str = Form(None)
):
    """
    Register a song in the database.

    Usage:
    curl -X POST "https://omi-webhook.onrender.com/register" \
      -F "file=@song.mp3" \
      -F "artist=Artist Name" \
      -F "title=Song Title"
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Rename file if artist and title provided (for metadata extraction)
        if artist and title:
            filename = f"1__{artist.replace(' ', '-')}__{title.replace(' ', '-')}{os.path.splitext(file.filename)[1]}"
            new_path = os.path.join(os.path.dirname(tmp_path), filename)
            os.rename(tmp_path, new_path)
            tmp_path = new_path

        # Register song using song_recogniser
        cmd = ['song_recogniser', 'register', tmp_path]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=ABRACADABRA_PATH,
            timeout=120
        )

        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

        if result.returncode == 0:
            logger.info(f"✅ Song registered: {artist or 'Unknown'} - {title or 'Unknown'}")
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Song registered: {artist or 'Unknown'} - {title or 'Unknown'}",
                    "artist": artist,
                    "title": title
                },
                status_code=200
            )
        else:
            logger.error(f"Failed to register song: {result.stderr}")
            return JSONResponse(
                content={
                    "status": "error",
                    "message": result.stderr,
                    "output": result.stdout
                },
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error registering song: {e}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


@app.get("/songs")
async def list_songs():
    """
    List all registered songs in the database.
    """
    try:
        import sqlite3
        db_path = os.path.join(ABRACADABRA_PATH, 'abracadabra.db')

        if not os.path.exists(db_path):
            return JSONResponse(
                content={"status": "error", "message": "Database not initialized"},
                status_code=404
            )

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT artist, album, title FROM song_info")
        songs = cursor.fetchall()
        conn.close()

        return JSONResponse(
            content={
                "status": "success",
                "count": len(songs),
                "songs": [
                    {"artist": s[0], "album": s[1], "title": s[2]}
                    for s in songs
                ]
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error listing songs: {e}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
