# YouTube Playlist Downloader

A Python console application that downloads videos from YouTube playlists as MP3 files and keeps track of downloaded files to ensure your collection stays up to date.

## Features

- Download individual YouTube videos as MP3 files
- Download entire YouTube playlists as MP3 files
- Track playlists to check for new videos at configurable intervals
- Maintain a history of downloaded videos to avoid duplicates
- Convert downloaded audio to different formats if needed
- Command-line interface with menu-driven interaction

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/youtube-playlist-downloader.git
   cd youtube-playlist-downloader
   ```

2. Create a virtual environment and activate it:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg (required for audio conversion):
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` or equivalent

## Usage

### Running the application

```bash
# Run with interactive menu
python main.py

# Download a single video
python main.py --download "https://www.youtube.com/watch?v=VIDEO_ID"

# Download a playlist
python main.py --download "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Add a playlist to track
python main.py --add-playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# List tracked playlists
python main.py --list-playlists

# Update all tracked playlists
python main.py --update-all

# Remove a playlist from tracking
python main.py --remove-playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Command-line options

```
usage: main.py [-h] [--download URL] [--add-playlist URL] [--list-playlists]
               [--update-all] [--remove-playlist URL] [--config FILE]
               [--output-dir DIR] [--check-interval HOURS]
               [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
               [--log-file FILE]

options:
  -h, --help            Show this help message and exit
  --download URL, -d URL
                        Download a YouTube video or playlist
  --add-playlist URL, -a URL
                        Add a playlist to track
  --list-playlists, -l  List all tracked playlists
  --update-all, -u      Update all tracked playlists
  --remove-playlist URL, -r URL
                        Remove a playlist from tracking
  --config FILE, -c FILE
                        Path to configuration file (default: config.ini)
  --output-dir DIR, -o DIR
                        Directory to save downloaded files
  --check-interval HOURS
                        How often to check for updates (in hours)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level
  --log-file FILE       File to log to (in addition to console)
```

## Configuration

The application uses a configuration file (`config.ini`) to store settings. This file is automatically created with default values on first run, or you can create it manually.

Example configuration:

```ini
[general]
output_directory = data/audio
check_interval = 24
max_downloads = 10

[audio]
format = mp3
bitrate = 192k
normalize_audio = True
target_level = -18.0

[logging]
level = INFO
file = app.log
console = True
```

## Project Structure

```
youtube-playlist-downloader/
├── downloader/
│   ├── __init__.py
│   ├── converter.py
│   ├── tracker.py
│   └── youtube.py
├── utils/
│   ├── __init__.py
│   ├── config_handler.py
│   └── file_manager.py
├── .gitignore
├── README.md
├── main.py
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader
- [pydub](https://github.com/jiaaro/pydub) - Audio processing
- [FFmpeg](https://ffmpeg.org/) - Audio/video conversion