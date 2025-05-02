# YouTube Playlist Downloader

A simple application that downloads videos from YouTube playlists as audio files and keeps track of downloaded files to ensure your collection stays up to date. Designed to be easy to use for non-programmers.

## ⚠️ Legal Disclaimer

This software is provided for educational and personal use only. The developer(s) of this application:

1. Do not endorse or encourage the unauthorized downloading of copyrighted content
2. Are not responsible for how users choose to use this software
3. Accept no liability for misuse of this software or any consequences thereof
4. Make no guarantees regarding the legality of downloading specific content

**Users are solely responsible for:**
- Ensuring they have the right to download any content
- Complying with YouTube's Terms of Service
- Following all applicable copyright laws in their jurisdiction
- Using downloaded content in accordance with fair use principles

Remember that downloading copyrighted material without permission may be illegal in your country. This tool should only be used for downloading content that is either in the public domain, licensed under permissive terms, or for which you have obtained proper permission.

## 📋 Features

- Download individual YouTube videos as audio files (MP3, WAV, OGG, M4A)
- Download entire YouTube playlists with automatic organization into folders
- Track playlists to check for new videos at configurable intervals
- Maintain a history of downloaded videos to avoid duplicates
- Convert audio to different formats with customizable bitrate
- Normalize audio levels for consistent volume across tracks
- Easy-to-use GUI for managing playlists and settings
- Console interface for automation and advanced users

## 🔧 Installation

### Prerequisites

1. **Python**: This application requires Python 3.8 or newer
   - Windows: [Download Python from python.org](https://www.python.org/downloads/windows/)
   - macOS: [Download Python from python.org](https://www.python.org/downloads/macos/)
   - Linux: Most distributions come with Python installed, or use your package manager

2. **FFmpeg**: Required for audio conversion
   - Windows: The installer will try to download and configure FFmpeg automatically
   - macOS: `brew install ffmpeg` (requires [Homebrew](https://brew.sh/))
   - Linux: `sudo apt install ffmpeg` or equivalent for your distribution

### Installation Steps

1. Download this repository:
   - Click the green "Code" button at the top of the page
   - Select "Download ZIP"
   - Extract the ZIP file to a folder on your computer

2. Run the installer script:
   - **Windows**: Double-click the `installer.py` file or right-click and select "Open with Python"
   - **macOS/Linux**: Open a terminal in the extracted folder and run:
     ```bash
     python3 installer.py
     ```

3. The installer will:
   - Create a virtual environment to isolate the application
   - Install all required dependencies
   - Set up FFmpeg for audio processing
   - Create launcher scripts for easy startup

## 🚀 Using the Application

### Starting the Application

After installation, you can start the application using:

- **Windows**:
  - GUI: Double-click `run_gui.bat`
  - Console: Double-click `run_console.bat`

- **macOS/Linux**:
  - GUI: Open a terminal and run `./run_gui.sh`
  - Console: Open a terminal and run `./run_console.sh`

### GUI Interface

The GUI provides a user-friendly way to:
- Add and manage YouTube playlists
- Configure audio settings (format, bitrate, etc.)
- Download individual videos
- Update all tracked playlists at once

### Console Interface

The console provides more advanced functionality:

```bash
# Download a single video
run_console.bat --download "https://www.youtube.com/watch?v=VIDEO_ID"

# Download a playlist
run_console.bat --download "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Add a playlist to track for updates
run_console.bat --add-playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# List tracked playlists
run_console.bat --list-playlists

# Update all tracked playlists (download new videos)
run_console.bat --update-all
```

Replace `.bat` with `.sh` on macOS/Linux.

## ⚙️ Configuration

The application uses a configuration file (`config.ini`) to store settings. You can edit this through the GUI or directly in a text editor:

```ini
[general]
output_directory = data/audio  # Where audio files are saved
check_interval = 24            # Hours between checks for new videos
max_downloads = 10             # Max videos to download per run

[audio]
format = mp3                   # Audio format (mp3, wav, m4a, ogg)
bitrate = 192k                 # Audio quality
normalize_audio = True         # Balance volume levels
target_level = -18.0           # Target volume level in dB

[logging]
level = INFO                   # Log detail level
file = app.log                 # Log file location
console = True                 # Show logs in console
```

## 🔍 Troubleshooting

- **FFmpeg errors**: If audio conversion fails, ensure FFmpeg is installed correctly
- **Download errors**: Some videos may be restricted and cannot be downloaded
- **GUI doesn't start**: Ensure tkinter is installed with Python
- **Playlist errors**: Make sure playlist URLs are correct and playlists are not private

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader
- [pydub](https://github.com/jiaaro/pydub) - Audio processing
- [FFmpeg](https://ffmpeg.org/) - Audio/video conversion