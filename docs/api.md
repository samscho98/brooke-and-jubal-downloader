# YouTube Playlist Downloader - API Documentation

## Core Modules

### Downloader API

#### `YouTubeDownloader`

```python
from downloader.youtube import YouTubeDownloader

# Initialize
downloader = YouTubeDownloader(output_dir="path/to/output")

# Download a single video
result = downloader.download_video("https://www.youtube.com/watch?v=VIDEO_ID")

# Get playlist videos without downloading
videos = downloader.get_playlist_videos("https://www.youtube.com/playlist?list=PLAYLIST_ID")

# Download a playlist
successful, failed = downloader.download_playlist("https://www.youtube.com/playlist?list=PLAYLIST_ID")
```

#### `AudioConverter`

```python
from downloader.converter import AudioConverter

# Convert to another format
output_file = AudioConverter.convert_audio("input.mp3", "wav")

# Normalize audio levels
AudioConverter.normalize_audio("input.mp3", target_level=-18.0)
```

#### `DownloadTracker`

```python
from downloader.tracker import DownloadTracker

# Initialize
tracker = DownloadTracker()

# Add playlist to track
tracker.add_playlist("https://www.youtube.com/playlist?list=PLAYLIST_ID", "My Playlist")

# Add a downloaded video to history
tracker.add_downloaded_video(video_id, playlist_id, title, file_path)

# Check for playlists that need updating
playlists_to_update = tracker.check_for_updates()
```

### Scoring API

#### `ScoreCalculator`

```python
from scoring.score_calculator import ScoreCalculator

# Initialize
calculator = ScoreCalculator()

# Calculate score for a video
score = calculator.calculate_score(video_id)

# Get top videos for a time slot
top_videos = calculator.get_top_videos(time_slot="US_PrimeTime", limit=10)
```

#### `QueueManager`

```python
from scoring.queue_manager import QueueManager

# Initialize
queue_manager = QueueManager()

# Create a queue
queue = queue_manager.create_queue(playlist_id=None, time_slot="US_PrimeTime")

# Get next item to play
next_item = queue_manager.get_next_item()
```

### Audio API

#### `AudioPlayer`

```python
from audio.player import AudioPlayer

# Initialize
player = AudioPlayer()

# Play an audio file
player.play("path/to/file.mp3")

# Control playback
player.pause()
player.resume()
player.stop()
player.set_volume(0.8)
```

## GUI Extension

To create custom views or components:

```python
from gui.views.base_view import BaseView

class MyCustomView(BaseView):
    def __init__(self, parent):
        super().__init__(parent)
        # Custom initialization
        
    def build_ui(self):
        # Create UI elements
        
    def on_show(self):
        # Called when view becomes visible
        
    def on_hide(self):
        # Called when view is hidden
```

## Event System

Subscribe to application events:

```python
from gui.event_bridge import EventBridge

# Subscribe to an event
EventBridge.subscribe("download_complete", self.on_download_complete)

# Publish an event
EventBridge.publish("playlist_added", {"playlist_id": "ID", "name": "New Playlist"})
```
