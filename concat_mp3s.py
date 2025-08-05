#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Combines all MP3 files in a given directory into a single MP3 file,
sorted alphabetically by filename, with a specified duration of silence
inserted between each track. The output path is configurable.
"""

import os
import sys
import argparse
from pydub import AudioSegment

### MODIFIED ###
# The function now accepts an `output_path` argument.
def combine_mp3s_with_pause(folder_path, pause_sec, output_path):
    """
    Finds, sorts, and combines MP3 files from a folder with silence in between.

    Args:
        folder_path (str): The path to the folder containing MP3 files.
        pause_sec (float): The duration of silence in seconds to add between files.
        output_path (str): The path for the final combined MP3 file.
    """
    # Validate the folder path
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'")
        sys.exit(1)

    ### ADDED ###
    # Validate the output path's directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        print(f"Error: The output directory '{output_dir}' does not exist.")
        print("Please create the directory or provide a valid path.")
        sys.exit(1)

    # Convert pause from seconds to milliseconds for pydub
    pause_ms = int(pause_sec * 1000)
    print(f"Using a pause of {pause_sec} seconds ({pause_ms} ms) between files.")

    # Create the silence segment
    silence = AudioSegment.silent(duration=pause_ms)

    # Find, filter, and sort all MP3 files in the directory
    try:
        mp3_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')])
    except Exception as e:
        print(f"Error reading directory: {e}")
        sys.exit(1)


    if not mp3_files:
        print(f"No MP3 files found in '{folder_path}'.")
        sys.exit(0)

    print(f"Found {len(mp3_files)} MP3 files to combine.")

    # --- Start combining ---
    print("Combining files...")
    
    # Initialize with the first file to avoid a leading pause
    first_file_path = os.path.join(folder_path, mp3_files[0])
    print(f"  (1/{len(mp3_files)}) Processing: {mp3_files[0]}")
    try:
        combined_audio = AudioSegment.from_mp3(first_file_path)
    except Exception as e:
        print(f"\nError: Could not process file '{mp3_files[0]}'. It may be corrupt or not a valid MP3.")
        print(f"Details: {e}")
        sys.exit(1)


    # Loop through the rest of the files, adding a pause before each one
    for i, filename in enumerate(mp3_files[1:], start=2):
        file_path = os.path.join(folder_path, filename)
        print(f"  ({i}/{len(mp3_files)}) Processing: {filename}")
        
        try:
            next_song = AudioSegment.from_mp3(file_path)
            # Add the silence, then the next song
            combined_audio += silence + next_song
        except Exception as e:
            print(f"\nError: Could not process file '{filename}'. It may be corrupt or not a valid MP3.")
            print(f"Details: {e}")
            # Optionally, you could 'continue' here to skip the broken file
            sys.exit(1)

    # --- Export the final combined audio ---
    ### MODIFIED ###
    # The hardcoded filename is replaced with the `output_path` argument.
    print(f"\nExporting to '{output_path}'...")
    
    try:
        # Export with a standard bitrate
        combined_audio.export(output_path, format="mp3", bitrate="192k")
    except Exception as e:
        print(f"Error exporting file: {e}")
        sys.exit(1)

    print("\n✅ Success! Your combined MP3 is ready.")
    ### MODIFIED ###
    # The success message now shows the absolute path of the specified output file.
    print(f"   Output file: {os.path.abspath(output_path)}")


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Combine MP3 files from a folder with pauses in between.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing your MP3 files."
    )
    parser.add_argument(
        "pause",
        type=float,
        help="The duration of silence in seconds to insert between files (e.g., 2.5)."
    )
    ### ADDED ###
    # This is the new third argument for the output file path.
    parser.add_argument(
        "output_file",
        help="Path for the final combined MP3 file (e.g., 'final_mix.mp3')."
    )

    args = parser.parse_args()
    
    # Basic validation for pause duration
    if args.pause < 0:
        print("Error: Pause duration cannot be negative.")
        sys.exit(1)

    ### ADDED ###
    # A simple check to ensure the output filename is an MP3.
    if not args.output_file.lower().endswith('.mp3'):
        print("Warning: The output file path does not end with .mp3.")
        print("The script will still attempt to export as an MP3 file.")


    try:
        ### MODIFIED ###
        # Pass the new argument to the main function.
        combine_mp3s_with_pause(args.folder, args.pause, args.output_file)
    except FileNotFoundError:
        print("\n---")
        print("FATAL ERROR: `ffmpeg` or `ffprobe` not found.")
        print("This script requires FFmpeg to be installed and accessible in your system's PATH.")
        print("Please install it from https://ffmpeg.org/download.html and try again.")
        print("---\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
