# YouTube Playlist Downloader - Usage Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-playlist-downloader.git
cd youtube-playlist-downloader

# Install requirements
pip install -r requirements.txt
```

## GUI Mode

```bash
python gui_main.py
```

The GUI provides these main sections:

- **Dashboard**: Overview of playlists and recent downloads
- **Playlists**: Manage and download playlists
- **Player**: Audio player with intelligent queues
- **Settings**: Configure application settings
- **Updates**: Check for and install updates

### Adding a Playlist

1. Navigate to the Playlists section
2. Enter the playlist URL and name
3. Click "Add Playlist"

### Downloading Videos

1. Select a playlist
2. Click "Download Now" or wait for automatic checking

### Playing Audio

1. Navigate to the Player section
2. Select a playlist or smart queue
3. Use playback controls to play/pause/skip

## Command Line Mode

```bash
python cli_main.py [command] [options]
```

Available commands:

```
add         Add a playlist to track
download    Download a playlist
list        List tracked playlists
update      Update all tracked playlists
play        Play audio files
config      Manage configuration
```

Examples:

```bash
# Add a playlist
python cli_main.py add "https://www.youtube.com/playlist?list=PLAYLIST_ID" "My Playlist"

# Download a playlist
python cli_main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Update all playlists
python cli_main.py update
```

## Configuration

Edit `config.ini` directly or use the Settings section in the GUI.

Key settings:

- `output_directory`: Where audio files are saved
- `check_interval`: How often to check for new videos (hours)
- `format`: Audio format (mp3, wav, etc.)
- `bitrate`: Audio quality
- `normalize_audio`: Whether to normalize audio levels

## Advanced Usage

See the detailed documentation in the `docs` directory for information on:

- Scoring algorithms and customization
- Command-line automation
- Custom audio processing
