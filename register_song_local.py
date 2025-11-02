#!/usr/bin/env python3
"""
Local script to register songs to Supabase
This allows you to register songs locally and have them available on Render
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from abracadabra import fingerprint
from abracadabra.recognise import get_song_info
import supabase_storage

def register_song_local(filepath: str, artist: str = None, title: str = None):
    """
    Register a song to Supabase from local file.
    
    Args:
        filepath: Path to the audio file
        artist: Artist name (optional, will try to extract from metadata)
        title: Song title (optional, will try to extract from metadata)
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    if not supabase_storage.supabase:
        print("❌ Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in .env")
        return False
    
    print(f"📁 Processing: {filepath}")
    
    try:
        # Generate fingerprints
        print("🔍 Generating fingerprints...")
        song_fingerprints = fingerprint.fingerprint_file(filepath)
        
        if not song_fingerprints:
            print("❌ Failed to generate fingerprints")
            return False
        
        print(f"✅ Generated {len(song_fingerprints)} fingerprints")
        
        # Get song info from metadata or filename
        song_info = get_song_info(filepath)
        artist_meta, album_meta, title_meta = song_info
        
        # Use provided metadata or fallback to extracted
        final_artist = artist or artist_meta or "Unknown"
        final_album = album_meta or "Unknown"
        final_title = title or title_meta or Path(filepath).stem
        
        print(f"🎵 Song: {final_artist} - {final_title}")
        print(f"💿 Album: {final_album}")
        
        # Generate song ID (matches what the webhook does)
        song_id = supabase_storage.get_song_id_from_path(filepath)
        print(f"🆔 Song ID: {song_id}")
        
        # Store in Supabase
        print("📤 Uploading to Supabase...")
        success = supabase_storage.store_song_complete(
            song_id, song_fingerprints, final_artist, final_album, final_title
        )
        
        if success:
            print("✅ Song registered successfully!")
            return True
        else:
            print("❌ Failed to store song in Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_registered_songs():
    """List all songs registered in Supabase"""
    if not supabase_storage.supabase:
        print("❌ Supabase not configured")
        return
    
    songs = supabase_storage.list_all_songs_supabase()
    
    if not songs:
        print("📭 No songs registered yet")
        return
    
    print(f"📚 {len(songs)} song(s) registered:")
    for i, (artist, album, title) in enumerate(songs, 1):
        print(f"{i}. {artist} - {title} ({album})")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Register songs to Supabase")
    parser.add_argument("command", choices=["register", "list"], help="Command to execute")
    parser.add_argument("--file", help="Path to audio file (for register command)")
    parser.add_argument("--artist", help="Artist name (optional)")
    parser.add_argument("--title", help="Song title (optional)")
    
    args = parser.parse_args()
    
    if args.command == "register":
        if not args.file:
            print("❌ --file is required for register command")
            sys.exit(1)
        
        success = register_song_local(args.file, args.artist, args.title)
        sys.exit(0 if success else 1)
        
    elif args.command == "list":
        list_registered_songs()
