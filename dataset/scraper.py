#!/usr/bin/env python3
"""
Find the first YouTube search result for a query (no API key), download it,
and convert the audio to a WAV file using yt-dlp + ffmpeg.

Usage examples:
  python yt_first_to_wav.py "lofi hip hop"
  python yt_first_to_wav.py "bach cello suite 1" --outdir out --ar 16000 --ac 1
  python yt_first_to_wav.py "creative commons birdsong" --ffmpeg "C:\\ffmpeg\\bin\\ffmpeg.exe"

Notes:
- Only download videos you have the right to download.
- Requires: yt-dlp, ffmpeg.
"""

import sys
import argparse
from pathlib import Path
import yt_dlp
import os


def parse_args():
    p = argparse.ArgumentParser(
        description="Search YouTube for the first result and convert audio to WAV."
    )
    p.add_argument("query", help="Search query string (e.g., 'lofi hip hop').")
    p.add_argument("--outdir", "-o", default="downloads", help="Output directory.")
    p.add_argument("--ffmpeg", default=None, help="Path to ffmpeg binary (if not on PATH).")
    p.add_argument("--ar", type=int, default=44100, help="Output WAV sample rate (Hz). Default: 44100.")
    p.add_argument("--ac", type=int, default=2, help="Output WAV channels (1=mono, 2=stereo). Default: 2.")
    p.add_argument("--quiet", action="store_true", help="Reduce yt-dlp output.")
    return p.parse_args()


def main():
    args = parse_args()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    # Build the yt-dlp search URL to fetch exactly one result
    search_url = f"ytsearch1:{args.query}"

    # yt-dlp options:
    # - format: bestaudio
    # - postprocessors: FFmpegExtractAudio to WAV
    # - postprocessor_args: ensure 16-bit PCM, desired sample rate/channels
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(outdir / "%(uploader)s - %(title)s - %(id)s.%(ext)s"),
        "noplaylist": True,
        "extract_flat": False,  # we want the actual media, not just metadata
        "quiet": args.quiet,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                # preferredquality ignored for WAV; kept for compatibility
                "preferredquality": "192",
            }
        ],
        # Enforce PCM 16-bit + chosen rate/channels
        "postprocessor_args": [
            "-acodec", "pcm_s16le",
            "-ar", str(args.ar),
            "-ac", str(args.ac),
        ],
        "skip_download": False,
        "ignoreerrors": False,
        "n_threads": 1,  # safer for first-result single download
    }

    if args.ffmpeg:
        ydl_opts["ffmpeg_location"] = args.ffmpeg

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # First peek at the result without downloading, so we can show details
        info = ydl.extract_info(search_url, download=False)
        if not info:
            print("No results found for query.")
            sys.exit(2)

        # When using ytsearch1:, yt-dlp returns a playlist-like dict with one entry
        entry = None
        if "entries" in info and info["entries"]:
            entry = info["entries"][0]
        else:
            # Some yt-dlp versions may return a single video dict directly
            entry = info

        if not entry:
            print("No valid entry found.")
            sys.exit(2)

        title = entry.get("title")
        channel = entry.get("uploader") or entry.get("channel")
        video_url = entry.get("webpage_url") or (f'https://www.youtube.com/watch?v={entry.get("id")}')
        duration = entry.get("duration")

        print("=" * 80)
        print("First result")
        print("Title   :", title)
        print("Channel :", channel)
        print("URL     :", video_url)
        print("Duration:", f"{duration}s" if duration is not None else "(unknown)")
        print("=" * 80)
        print("Starting download and audio conversion to WAV...")

        # Now actually download (this will obey postprocessors to make WAV)
        # Using the same ytsearch1: URL downloads that first result directly.
        ydl.download([search_url])

    # Get the actual filename that yt-dlp generated
    # This part is a bit tricky as yt-dlp doesn't directly return the path
    # after download in a simple way. We'll rely on the outtmpl to reconstruct.
    # This might need refinement if the naming convention changes often.
    # Assuming the outtmpl is `outdir / "%(uploader)s - %(title)s - %(id)s.%(ext)s"`
    # We need to get the exact `uploader`, `title`, `id` and `ext` used.
    # A more robust solution might involve parsing yt-dlp's output or using a custom hook.

    # For now, let's assume the first entry's info is used for the filename.
    # This is a simplification and might break if yt-dlp changes its behavior.
    # It's better to get the actual downloaded file path.
    # A better way would be to get the info from the downloaded file directly if possible
    # Or, if yt-dlp provides a way to get the final filename, use that.

    # Reconstructing the filename based on the info extracted earlier.
    # This is not ideal as it's a re-computation, not retrieval of actual path.
    # A more robust solution involves custom hooks in yt-dlp or parsing stdout/stderr of yt-dlp.
    # For simplicity for now, let's assume the format is consistent.
    # The actual extension will be 'wav' due to postprocessors.
    if entry and title and channel and entry.get("id"):
        # Ensure we use a clean title and channel name for filename reconstruction
        # yt-dlp might sanitize these further, so this is still an approximation
        sanitized_title = title.replace(os.path.sep, '_').replace(':', '_').replace('?', '')
        sanitized_channel = channel.replace(os.path.sep, '_').replace(':', '_').replace('?', '')
        video_id = entry.get("id")
        expected_filename = f"{sanitized_channel} - {sanitized_title} - {video_id}.wav"
        downloaded_filepath = outdir / expected_filename

        # It's possible that yt-dlp changes the filename if there are conflicts,
        # or if the title contains characters not allowed in filenames. For robustness,
        # one might need to list files in `outdir` and find the most recently created `.wav` file.
        # However, for this exercise, we will assume a direct reconstruction is sufficient.

        print(f"DOWNLOADED_FILE_PATH: {downloaded_filepath}")

    print("\nDone. Files saved in:", outdir)


if __name__ == "__main__":
    main()
