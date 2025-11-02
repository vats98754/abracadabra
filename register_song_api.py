#!/usr/bin/env python3
"""
API endpoint to register songs on Render
Add this to your omi_song_recognition_webhook.py to enable song registration via API
"""

from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
import os
import subprocess

# Add this endpoint to your omi_song_recognition_webhook.py:

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
