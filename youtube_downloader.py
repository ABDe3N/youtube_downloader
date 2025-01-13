# YouTube Video and Playlist Downloader
# This script provides a flexible solution for downloading YouTube content
# using yt-dlp, with support for various download options.

# Import required libraries for system interaction, JSON parsing, 
# progress tracking, and colored output
import subprocess  # For running shell commands
import argparse    # For parsing command-line arguments
import re          # For regular expression operations (potential future use)
import json        # For parsing JSON output from yt-dlp
from tqdm import tqdm  # For creating interactive progress bars
import sys         # For system-specific parameters
from colorama import init, Fore, Style  # For adding color to terminal output
import os          # For creating directories

# Initialize colorama for cross-platform colored terminal output
init()

def is_playlist(url):
    """Check if the URL is a playlist."""
    return 'playlist' in url or '&list=' in url

def parse_video_range(range_str):
    """Parse video range from format like '5:21' to start and end numbers."""
    if not range_str:
        return None, None
    try:
        if ':' in range_str:
            start, end = map(int, range_str.split(':'))
            return start, end
        else:
            # If only one number is provided, use it as both start and end
            num = int(range_str)
            return num, num
    except ValueError:
        raise argparse.ArgumentTypeError("Video range must be in format 'start:end' or single number")

def parse_quality(quality_str):
    """Parse video quality from format like '360' or '1080'."""
    if not quality_str:
        return None
    try:
        quality = int(quality_str)
        valid_qualities = [144, 240, 360, 480, 720, 1080, 1440, 2160]
        if quality not in valid_qualities:
            raise argparse.ArgumentTypeError(
                f"Invalid quality. Choose from: {', '.join(map(str, valid_qualities))}"
            )
        return quality
    except ValueError:
        raise argparse.ArgumentTypeError("Quality must be a number (e.g., 360, 1080)")

def format_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:3.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}TB"

def download_video_yt_dlp(url, output_path, audio_only=False, playlist_start=None, playlist_end=None, quality=None, download_transcript=False, transcript_lang=None):
    """Downloads a YouTube video or playlist using yt-dlp."""
    try:
        # Construct yt-dlp command with dynamic options
        command = [
            "yt-dlp",
            url,
            "-o",
            f"{output_path}/%(title)s.%(ext)s",
            "--print-json",  # Detailed video information
            "--progress",    # Enable progress reporting
            "--newline"      # Ensure clean output
        ]

        # Add transcript download options if requested
        if download_transcript:
            command.extend([
                "--write-auto-subs",  # Also try auto-generated subtitles if manual ones aren't available
                "--write-subs",       # Download subtitles
                "--sub-format", "srt",  # Prefer SRT format
                "--convert-subs", "srt"  # Convert subtitles to SRT
            ])
            if transcript_lang:
                command.extend(["--sub-lang", transcript_lang])
            else:
                command.extend(["--sub-lang", "en,ar"])  # Default to English and Arabic

        # Configure audio or video download
        if audio_only:
            # Extract high-quality audio as MP3
            command.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
        elif quality:
            # Select video with specified maximum quality
            command.extend([
                "-f", f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
            ])
        
        # Add playlist range selection
        if playlist_start is not None:
            command.extend(["--playlist-start", str(playlist_start)])
        if playlist_end is not None:
            command.extend(["--playlist-end", str(playlist_end)])

        # Playlist download notification
        total_items = None
        current_item = None
        relative_counter = 0  # Add counter for relative position
        if is_playlist(url):
            if playlist_start is not None and playlist_end is not None:
                total_items = playlist_end - playlist_start + 1
            print("Downloading playlist...")

        # Create subprocess for command execution
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Initialize tracking variables
        pbar = None
        current_title = None
        downloading_started = False
        file_size = None
        downloaded_size = None

        # Process output line by line
        for line in process.stdout:
            line = line.strip()
            
            try:
                # Parse JSON output for video details
                data = json.loads(line)
                
                # Extract video metadata
                current_title = data.get('title', 'Unknown Title')
                format_id = data.get('format_id', 'N/A')
                video_ext = data.get('ext', 'N/A')
                
                # Get video quality information
                vcodec = data.get('vcodec', 'none')
                acodec = data.get('acodec', 'none')
                
                height = data.get('height', 'N/A')
                abr = data.get('abr', 'N/A')
                
                # Determine file size
                if 'filesize' in data and data['filesize']:
                    file_size = data['filesize']
                elif 'filesize_approx' in data and data['filesize_approx']:
                    file_size = data['filesize_approx']
                
                # Update playlist information
                if '_type' in data and data['_type'] == 'playlist':
                    if 'entries' in data:
                        total_items = len(data['entries'])
                
                # Display download information
                print()  # Spacing
                if total_items:
                    relative_counter += 1  # Increment download counter
                    print(f"Downloading item {Fore.CYAN}{relative_counter}{Style.RESET_ALL} of {Fore.GREEN}{total_items}{Style.RESET_ALL}")
                
                # Print detailed video information
                print(f"Downloading: {current_title}")
                if vcodec != 'none':
                    print(f"Video Quality: {height}p")
                if acodec != 'none':
                    print(f"Audio Bitrate: {abr}k")
                print(f"File Extension: {video_ext}")
                if file_size:
                    print(f"File Size: {format_size(file_size)}")
                
                # Create progress bar
                if pbar:
                    pbar.close()
                pbar = tqdm(
                    total=100,
                    desc="Progress",
                    bar_format='{desc}: {percentage:3.0f}%|{bar}| {n:.1f}/{total:.1f} ' + 
                    (f'[{format_size(file_size)}]' if file_size else '')
                )
                downloading_started = True
                
            except json.JSONDecodeError:
                # Handle progress updates
                if downloading_started and pbar:
                    if "[download]" in line:
                        try:
                            # Extract and update progress percentage
                            if "%" in line:
                                percent = float(line.split("%")[0].split()[-1])
                                pbar.n = percent
                                
                                # Update progress description with current size
                                if "iB" in line and "iB/" in line:
                                    size_part = line.split()[3]  # Get the size part (e.g., "1.2MiB/5.4MiB")
                                    if "/" in size_part:
                                        current_size = size_part.split("/")[0]
                                        total_size = size_part.split("/")[1]
                                        pbar.set_description(f"Progress [{current_size}/{total_size}]")
                                pbar.refresh()
                        except (ValueError, IndexError):
                            pass

        # Close final progress bar
        if pbar:
            pbar.close()

        # Wait for process completion
        process.wait()

        # Check for errors
        if process.returncode != 0:
            error_output = process.stderr.read()
            print(f"Error occurred: {error_output}")
            return

        # Download completion message
        print(f"\n{Fore.GREEN}Download Complete!{Style.RESET_ALL}")
        
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        if process:
            process.kill()

def main():
    """Main function to handle command line arguments and initiate download."""
    parser = argparse.ArgumentParser(description="Download YouTube videos and playlists")
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument("-o", "--output", default=".", help="Output directory path")
    parser.add_argument("-a", "--audio", action="store_true", help="Download audio only")
    parser.add_argument("-r", "--range", type=parse_video_range, help="Video range for playlists (e.g., '5:10')")
    parser.add_argument("-q", "--quality", type=parse_quality, help="Maximum video quality (e.g., 360, 1080)")
    parser.add_argument("-t", "--transcript", action="store_true", help="Download video transcript/subtitles")
    parser.add_argument("-l", "--lang", help="Language code for transcript (e.g., 'en' for English, 'ar' for Arabic)")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    try:
        start, end = None, None
        if args.range:
            start, end = args.range

        download_video_yt_dlp(
            args.url,
            args.output,
            audio_only=args.audio,
            playlist_start=start,
            playlist_end=end,
            quality=args.quality,
            download_transcript=args.transcript,
            transcript_lang=args.lang
        )
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

# Entry point of the script
if __name__ == "__main__":
    main()