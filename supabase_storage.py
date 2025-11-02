#!/usr/bin/env python3
"""
Supabase storage backend for abracadabra
Stores songs and fingerprints in Supabase PostgreSQL instead of local SQLite
"""

import os
from supabase import create_client, Client
from typing import Optional, List, Tuple

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

# SQL schema for Supabase tables
# Based on abracadabra's SQLite structure with PostgreSQL-safe naming:
#   SQLite "hash" table → Supabase "hashes" table
#   SQLite "hash" column → Supabase "fingerprint_hash" column (avoids keyword)
SCHEMA_SQL = """
-- song_info table
CREATE TABLE IF NOT EXISTS song_info (
    artist TEXT,
    album TEXT,
    title TEXT,
    song_id TEXT
);

-- hashes table (avoids "hash" keyword)
-- IMPORTANT: offset is DOUBLE PRECISION (not INTEGER) for floating-point time values
CREATE TABLE IF NOT EXISTS hashes (
    fingerprint_hash BIGINT NOT NULL,
    offset DOUBLE PRECISION NOT NULL,
    song_id TEXT NOT NULL
);

-- Index for fast lookup
CREATE INDEX IF NOT EXISTS idx_fingerprint_hash ON hashes(fingerprint_hash);
"""

def init_supabase_tables():
    """Initialize Supabase tables if they don't exist"""
    if not supabase:
        print("⚠️  Supabase not configured")
        return False

    try:
        # Note: You'll need to run the schema SQL manually in Supabase SQL editor
        # Or use Supabase migrations
        print("✅ Supabase connected")
        print("📝 Run this SQL in Supabase SQL Editor to create tables:")
        print(SCHEMA_SQL)
        return True
    except Exception as e:
        print(f"❌ Supabase initialization error: {e}")
        return False

def store_song_supabase(song_id: str, artist: str, album: str, title: str):
    """Store song metadata in Supabase"""
    if not supabase:
        return False

    try:
        data = {
            "song_id": song_id,
            "artist": artist,
            "album": album,
            "title": title
        }
        result = supabase.table("song_info").upsert(data).execute()
        return True
    except Exception as e:
        print(f"Error storing song: {e}")
        return False

def store_fingerprints_supabase(song_id: str, fingerprints: List[Tuple[int, int]]):
    """Store fingerprints in Supabase"""
    if not supabase:
        return False

    try:
        # Batch insert fingerprints
        data = [
            {
                "fingerprint_hash": fp_hash,
                "offset": time_offset,
                "song_id": song_id
            }
            for fp_hash, time_offset in fingerprints
        ]

        # Insert in batches of 1000
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            supabase.table("hashes").insert(batch).execute()

        return True
    except Exception as e:
        print(f"Error storing fingerprints: {e}")
        return False

def get_song_by_id_supabase(song_id: str) -> Optional[Tuple[str, str, str]]:
    """Get song metadata from Supabase"""
    if not supabase:
        return None

    try:
        result = supabase.table("song_info").select("*").eq("song_id", song_id).execute()
        if result.data and len(result.data) > 0:
            song = result.data[0]
            return (song['artist'], song['album'], song['title'])
        return None
    except Exception as e:
        print(f"Error getting song: {e}")
        return None

def list_all_songs_supabase() -> List[Tuple[str, str, str]]:
    """List all songs from Supabase"""
    if not supabase:
        return []

    try:
        result = supabase.table("song_info").select("artist,album,title").execute()
        return [(s['artist'], s['album'], s['title']) for s in result.data]
    except Exception as e:
        print(f"Error listing songs: {e}")
        return []


def get_matches_supabase(fingerprints: List[Tuple[int, int]]) -> List[str]:
    """
    Match fingerprints against database and return list of matching song_ids.

    Args:
        fingerprints: List of (hash, time_offset) tuples

    Returns:
        List of song_ids that match the fingerprints
    """
    if not supabase:
        return []

    try:
        # Extract just the hashes for matching
        hash_values = [fp[0] for fp in fingerprints]

        # Query database for matching hashes (batch query)
        # Note: Supabase has a limit on IN clause size, so we batch if needed
        batch_size = 1000
        all_matches = []

        for i in range(0, len(hash_values), batch_size):
            batch_hashes = hash_values[i:i+batch_size]
            result = supabase.table("hashes").select("song_id").in_("fingerprint_hash", batch_hashes).execute()

            if result.data:
                all_matches.extend([row['song_id'] for row in result.data])

        return all_matches
    except Exception as e:
        print(f"Error matching fingerprints: {e}")
        return []


def get_song_info_supabase(song_id: str) -> Optional[Tuple[str, str, str]]:
    """Get song metadata (artist, album, title) from Supabase"""
    return get_song_by_id_supabase(song_id)


def get_song_id_from_path(filepath: str) -> str:
    """
    Generate a unique song ID from filepath.
    Uses the same logic as abracadabra.storage.get_song_id()
    """
    import hashlib
    from pathlib import Path

    # Use filename as basis for song ID
    filename = Path(filepath).name
    return hashlib.md5(filename.encode()).hexdigest()


def store_song_complete(song_id: str, fingerprints: List[Tuple[int, int]],
                       artist: str, album: str, title: str) -> bool:
    """
    Store both song metadata and fingerprints in Supabase.

    Args:
        song_id: Unique identifier for the song
        fingerprints: List of (hash, time_offset) tuples
        artist: Artist name
        album: Album name
        title: Song title

    Returns:
        True if successful, False otherwise
    """
    if not supabase:
        print("⚠️  Supabase not configured")
        return False

    try:
        # Store song metadata
        success = store_song_supabase(song_id, artist, album, title)
        if not success:
            return False

        # Store fingerprints
        success = store_fingerprints_supabase(song_id, fingerprints)
        return success
    except Exception as e:
        print(f"Error storing song: {e}")
        return False


def get_all_songs_supabase() -> List[Tuple[str, str, str]]:
    """Alias for list_all_songs_supabase for compatibility"""
    return list_all_songs_supabase()
