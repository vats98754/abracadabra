import pandas as pd
import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import threading

# Global lock for file writing
file_lock = threading.Lock()

def get_track_names_from_csv(csv_filepath):
    """Parses the CSV file and extracts unique track names along with their metadata.

    :param csv_filepath: Path to the CSV file.
    :return: A dictionary where keys are track names and values are dictionaries
             containing 'artist', 'album_name', and 'track_name'.
    :rtype: dict
    """
    df = pd.read_csv(csv_filepath)
    
    df = df.sort_values(by='popularity', ascending=False)
    # Drop rows where 'track_name' is NaN before processing
    df_cleaned = df.dropna(subset=['track_name'])
    
    track_metadata = {}
    for index, row in df_cleaned.iterrows():
        track_name = row['track_name']
        track_metadata[track_name] = {
            'artist': row.get('artists', 'Unknown Artist'),
            'album_name': row.get('album_name', 'Unknown Album'),
            'track_name': track_name
        }
    return track_metadata

def call_scraper_and_recognise(track_metadata, output_filepath):
    """Calls scraper.py, then song_recogniser, then deletes the WAV file.
    Metadata is written to the WAV file after download.
    """
    track_name = track_metadata['track_name'] + " song " + track_metadata["artist"] + " official audio"
    downloaded_filepath = None
    python_executable = sys.executable

    try:
        script_path = os.path.join(os.path.dirname(__file__), 'scraper.py')
        process = subprocess.run(
            [python_executable, script_path, track_name],
            check=True, capture_output=True, text=True
        )
        print(f"Successfully scraped: {track_name}")

        for line in process.stdout.splitlines():
            if line.startswith("DOWNLOADED_FILE_PATH:"):
                downloaded_filepath = line.split(": ", 1)[1].strip()
                break

        if downloaded_filepath and os.path.exists(downloaded_filepath):
            # Write metadata to the MP3 file
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, TIT2, TPE1, TALB
            try:
                audio = MP3(downloaded_filepath)
                # MP3 files natively support ID3.
                if audio.tags is None:
                    audio.tags = ID3()
                
                audio.tags.add(TIT2(encoding=3, text=[track_metadata['track_name']]))
                audio.tags.add(TPE1(encoding=3, text=[track_metadata['artist']]))
                audio.tags.add(TALB(encoding=3, text=[track_metadata['album_name']]))
                audio.tags.save(downloaded_filepath)
                print(f"Successfully wrote metadata to {downloaded_filepath}")
            except Exception as e:
                print(f"Error writing metadata to {downloaded_filepath}: {e}")
            
            print(f"Recognising song: {downloaded_filepath}")
            recognise_process = subprocess.run(
                [python_executable, '-m', 'abracadabra.scripts.song_recogniser', 'register', downloaded_filepath],
                check=True, capture_output=True, text=True
            )
            if recognise_process.stdout:
                print("Recognizer stdout:", recognise_process.stdout)
            if recognise_process.stderr:
                print("Recognizer stderr:", recognise_process.stderr)
            recognition_result = recognise_process.stdout.strip()
            print(f"Recognition result for {track_name}: {recognition_result}")

            # Write successful song title to file
            if recognition_result and "None" not in recognition_result: # Assuming 'None' means no recognition
                with file_lock:
                    with open(output_filepath, 'a') as f:
                        f.write(f"{track_name}\n")
                print(f"Logged successful recognition for: {track_name}")
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
        pass
        # if downloaded_filepath and os.path.exists(downloaded_filepath):
        #     try:
        #         os.remove(downloaded_filepath)
        #         print(f"Deleted MP3 file: {downloaded_filepath}")
        #     except OSError as e:
        #         print(f"Error deleting file {downloaded_filepath}: {e}")

def main():
    csv_filepath = './archive/dataset.csv' # Assuming this path relative to the project root
    output_filename = 'successful_recognitions.txt'
    output_filepath = os.path.join(os.path.dirname(__file__), output_filename)

    # Initialize the song recogniser database
    print("Initializing song recogniser database...")
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), '..', 'abracadabra', 'scripts', 'song_recogniser.py')
    subprocess.run([python_executable, script_path, 'initialise'], check=True)
    print("Song recogniser database initialized.")

    all_track_metadata = get_track_names_from_csv(csv_filepath)
    track_names_list = list(all_track_metadata.values())

    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        # Pass output_filepath to the concurrent function
        executor.map(lambda metadata: call_scraper_and_recognise(metadata, output_filepath), track_names_list)

if __name__ == "__main__":
    main() # End of script

