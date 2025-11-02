import pandas as pd
import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
import sys

def get_track_names_from_csv(csv_filepath):
    """Parses the CSV file and extracts unique track names."""
    df = pd.read_csv(csv_filepath)
    track_names = set(df['track_name'].dropna().unique())
    return track_names

def call_scraper_and_recognise(track_name):
    """Calls scraper.py, then song_recogniser, then deletes the WAV file."""
    downloaded_filepath = None
    # Get the path to the virtual environment's python executable
    python_executable = sys.executable

    try:
        script_path = os.path.join(os.path.dirname(__file__), 'scraper.py')
        # Capture the output of scraper.py
        process = subprocess.run(
            [python_executable, script_path, track_name],
            check=True, capture_output=True, text=True
        )
        print(f"Successfully scraped: {track_name}")

        # Parse the output to get the downloaded file path
        for line in process.stdout.splitlines():
            if line.startswith("DOWNLOADED_FILE_PATH:"):
                downloaded_filepath = line.split(": ", 1)[1].strip()
                break

        if downloaded_filepath and os.path.exists(downloaded_filepath):
            print(f"Recognising song: {downloaded_filepath}")
            # Call song_recogniser
            recognise_process = subprocess.run(
                [python_executable, '-m', 'abracadabra.scripts.song_recogniser', 'recognise', downloaded_filepath],
                check=True, capture_output=True, text=True
            )
            print(f"Recognition result for {track_name}: {recognise_process.stdout.strip()}")
        else:
            print(f"Error: Downloaded file path not found or file does not exist for {track_name}")

    except subprocess.CalledProcessError as e:
        print(f"Error processing {track_name}: {e}")
        if e.stdout:
            print("Scraper stdout:", e.stdout)
        if e.stderr:
            print("Scraper stderr:", e.stderr)
    except FileNotFoundError:
        print(f"Error: Scraper or song_recogniser script not found for {track_name}")
    finally:
        if downloaded_filepath and os.path.exists(downloaded_filepath):
            try:
                os.remove(downloaded_filepath)
                print(f"Deleted WAV file: {downloaded_filepath}")
            except OSError as e:
                print(f"Error deleting file {downloaded_filepath}: {e}")

def main():
    csv_filepath = './archive/dataset.csv' # Assuming this path relative to the project root
    track_names = get_track_names_from_csv(csv_filepath)

    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        executor.map(call_scraper_and_recognise, track_names)

if __name__ == "__main__":
    main() # End of script

