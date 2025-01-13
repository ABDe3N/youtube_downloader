# YouTube Video and Playlist Downloader

A powerful Python script for downloading YouTube videos and playlists with extensive customization options. Built on top of yt-dlp with enhanced features and user-friendly progress tracking.

## Features

- Download single videos or entire playlists
- Audio-only extraction option (MP3 format)
- Quality selection (144p to 4K)
- Playlist range selection
- Subtitle/transcript download support
- Real-time progress tracking with size information
- Colored terminal output for better visibility
- Support for multiple output formats

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic command structure:
```bash
python youtube_downloader.py [URL] [OPTIONS]
```

### Command-line Options

- `-o, --output`: Output directory path (default: current directory)
- `-a, --audio`: Download audio only (MP3 format)
- `-r, --range`: Video range for playlists (e.g., '5:10')
- `-q, --quality`: Maximum video quality (e.g., 360, 1080)
- `-t, --transcript`: Download video transcript/subtitles
- `-l, --lang`: Language code for transcript (e.g., 'en' for English, 'ar' for Arabic)

### Examples

1. Download a single video:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID
```

2. Download with specific quality:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -q 1080
```

3. Extract audio only:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -a
```

4. Download specific videos from a playlist:
```bash
python youtube_downloader.py https://www.youtube.com/playlist?list=PLAYLIST_ID -r 5:10
```

5. Download video with subtitles:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -t -l en
```

6. Download to specific directory:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -o "D:/Downloads/YouTube"
```

### Supported Video Qualities

- 144p
- 240p
- 360p
- 480p
- 720p
- 1080p
- 1440p
- 2160p (4K)

## Progress Information

The script provides detailed progress information including:
- Download progress percentage
- File size (both current and total)
- Video quality and format
- Audio bitrate (for audio downloads)
- Current item number when downloading playlists

## Error Handling

The script includes comprehensive error handling for:
- Invalid URLs
- Network issues
- Invalid quality selections
- Playlist range errors
- File system errors

## Requirements

- Python 3.6 or higher
- yt-dlp
- colorama
- tqdm

## Note

This script requires yt-dlp to be installed and accessible in your system's PATH. The script will automatically use the best available quality if no specific quality is selected.
