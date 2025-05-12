# Downloader Module

A module for downloading YouTube videos, managing download history, and processing audio files.

## Overview

The `downloader` module provides functionality for downloading videos and playlists from YouTube, tracking download history, converting audio formats, and implementing a scoring system for video recommendations.

## Classes and Methods

### YouTubeDownloader

Class to handle YouTube video downloading operations.

#### Methods

- `__init__(output_dir="data/audio", config=None)`: Initializes the YouTube downloader.
  - `output_dir`: Directory to save downloaded files
  - `config`: Optional configuration handler

- `get_video_info(video_url)`: Gets detailed information about a YouTube video.
  - `video_url`: URL of the YouTube video
  - Returns: Dictionary containing video information or None if retrieval failed

- `download_video(video_url, audio_only=True, playlist_name=None)`: Downloads a single video from YouTube.
  - `video_url`: URL of the YouTube video
  - `audio_only`: If True, download only the audio
  - `playlist_name`: Optional name of the playlist for organizing downloads
  - Returns: Tuple of (path to the downloaded file, video info dict) or None if download failed

- `get_playlist_videos(playlist_url)`: Gets information about all videos in a playlist without downloading them.
  - `playlist_url`: URL of the YouTube playlist
  - Returns: List of dictionaries containing video information

- `download_playlist(playlist_url, audio_only=True, playlist_name=None)`: Downloads all videos from a YouTube playlist.
  - `playlist_url`: URL of the YouTube playlist
  - `audio_only`: If True, download only the audio
  - `playlist_name`: Optional name of the playlist for organizing downloads
  - Returns: Tuple of (list of successful downloads, list of failed video IDs)

### AudioConverter

Class to handle audio conversion operations.

#### Supported Formats

The AudioConverter supports the following formats: `mp3`, `wav`, `ogg`, `m4a`, `flac`, `aac`

#### Methods

- `convert_audio(input_file, output_format="mp3", output_dir=None, bitrate="192k")`: Converts an audio file to the specified format.
  - `input_file`: Path to the input audio file
  - `output_format`: Desired output format
  - `output_dir`: Directory to save the output file (defaults to same as input)
  - `bitrate`: Audio bitrate for the output file
  - Returns: Path to the converted file or None if conversion failed

- `convert_to_mp3(input_file, output_dir=None, bitrate="192k")`: Converts an audio file to MP3 format.
  - `input_file`: Path to the input audio file
  - `output_dir`: Directory to save the output file (defaults to same as input)
  - `bitrate`: Audio bitrate for the output file
  - Returns: Path to the converted file or None if conversion failed

- `ffmpeg_convert(input_file, output_file, ffmpeg_args=None)`: Uses FFmpeg directly for more complex audio conversions or processing.
  - `input_file`: Path to the input audio file
  - `output_file`: Path to the output audio file
  - `ffmpeg_args`: Additional FFmpeg arguments
  - Returns: True if conversion succeeded, False otherwise

- `normalize_audio(input_file, output_file=None, target_level=-18.0)`: Normalizes audio levels in the file.
  - `input_file`: Path to the input audio file
  - `output_file`: Path to the output audio file (defaults to overwrite input)
  - `target_level`: Target audio level in dB
  - Returns: Path to the normalized file or None if normalization failed

### DownloadTracker

Class to track downloaded videos and manage playlists. This is a wrapper for the `EnhancedDownloadTracker` class.

#### Methods

- `__init__(history_file="download_history.json", playlists_file="playlists.json")`: Initializes the download tracker.
  - `history_file`: Path to the file storing download history
  - `playlists_file`: Path to the file storing playlist information

- `add_playlist(url, name=None, check_interval=24)`: Adds a new playlist to track.
  - `url`: URL of the playlist
  - `name`: Optional name for the playlist
  - `check_interval`: How often to check for updates (in hours)
  - Returns: True if added successfully, False otherwise

- `remove_playlist(url)`: Removes a playlist from tracking.
  - `url`: URL of the playlist to remove
  - Returns: True if removed successfully, False if not found

- `get_playlists()`: Gets all tracked playlists.
  - Returns: List of playlist dictionaries

- `update_playlist_check_time(url)`: Updates the last checked time for a playlist.
  - `url`: URL of the playlist
  - Returns: True if updated successfully, False if not found

- `add_downloaded_video(video_id, playlist_id, title, file_path, view_count=0, comment_count=0, upload_date=None, duration_seconds=0.0)`: Adds a downloaded video to the history.
  - `video_id`: YouTube video ID
  - `playlist_id`: YouTube playlist ID
  - `title`: Title of the video
  - `file_path`: Path to the downloaded file
  - `view_count`: Number of views the video has
  - `comment_count`: Number of comments the video has
  - `upload_date`: Date the video was uploaded (YYYYMMDD format)
  - `duration_seconds`: Duration of the video in seconds
  - Returns: True if added successfully, False otherwise

- `update_video_view_count(video_id, view_count)`: Updates the view count for a video.
  - `video_id`: YouTube video ID
  - `view_count`: Current view count
  - Returns: True if updated successfully, False otherwise

- `bulk_update_view_counts(downloader)`: Updates view counts for all videos in the history.
  - `downloader`: YouTubeDownloader instance to get video info
  - Returns: Tuple of (number of videos updated, number of failures)

- `is_video_downloaded(video_id)`: Checks if a video has already been downloaded.
  - `video_id`: YouTube video ID
  - Returns: True if the video is already downloaded, False otherwise

- `get_downloaded_videos(playlist_id=None)`: Gets all downloaded videos, optionally filtered by playlist.
  - `playlist_id`: Optional YouTube playlist ID to filter by
  - Returns: List of video dictionaries

- `get_video_stats()`: Gets statistics about the downloaded videos.
  - Returns: Dictionary with statistics

- `check_for_updates()`: Checks which playlists need to be updated based on their check interval.
  - Returns: List of playlists that need to be updated

### ScoringSystem

Class to handle video scoring and performance tracking.

#### Methods

- `__init__(scores_file="data/video_scores.json")`: Initializes the scoring system.
  - `scores_file`: Path to the file storing video scores

- `update_video_metadata(video_id, title, youtube_views, youtube_comments, upload_date=None, is_new_release=False)`: Updates basic metadata for a video and recalculates its base score.
  - `video_id`: YouTube video ID
  - `title`: Video title
  - `youtube_views`: Number of views on YouTube
  - `youtube_comments`: Number of comments on YouTube
  - `upload_date`: Optional upload date (YYYYMMDD format)
  - `is_new_release`: Whether this is a new release (< 14 days)
  - Returns: True if successful, False otherwise

- `record_stream_performance(video_id, time_slot, viewer_change, chat_messages, avg_viewers, returning_viewer_count, returning_viewer_percentage, returning_viewer_retention)`: Records performance metrics from a livestream play.
  - `video_id`: YouTube video ID
  - `time_slot`: Time slot label (e.g., "US_PrimeTime")
  - `viewer_change`: Change in viewers during playback
  - `chat_messages`: Number of chat messages during playback
  - `avg_viewers`: Average number of viewers during playback
  - `returning_viewer_count`: Number of viewers who have watched previous streams
  - `returning_viewer_percentage`: Percentage of total viewers who are returning
  - `returning_viewer_retention`: Percentage of returning viewers who stay
  - Returns: True if successful, False otherwise

- `get_top_videos(time_slot=None, playlist_id=None, limit=10, include_new_releases=True)`: Gets top scoring videos, optionally filtered by time slot or playlist.
  - `time_slot`: Optional time slot to filter by
  - `playlist_id`: Optional playlist ID to filter by
  - `limit`: Maximum number of videos to return
  - `include_new_releases`: Whether to include new releases regardless of score
  - Returns: List of video dictionaries with scores

- `get_current_time_slot()`: Determines the current time slot based on UTC time.
  - Returns: Current time slot label

- `update_playlist_performance(playlist_id, name, viewer_change)`: Updates performance metrics for a playlist.
  - `playlist_id`: YouTube playlist ID
  - `name`: Playlist name
  - `viewer_change`: Average viewer change during playback
  - Returns: True if successful, False otherwise

## Time Slots for Scoring

The scoring system defines the following time slots for optimizing video recommendations:

- **US_PrimeTime**: 22:00-03:00 UTC (Performance factor: 1.3)
- **UK_Evening**: 18:00-22:00 UTC (Performance factor: 1.1)
- **PH_Evening**: 10:00-16:00 UTC (Performance factor: 0.9)
- **Low_Traffic**: 03:00-10:00 UTC (Performance factor: 0.7)

## Usage Examples

### Downloading a Video

```python
from downloader.youtube import YouTubeDownloader

# Initialize the downloader
downloader = YouTubeDownloader(output_dir="downloads/audio")

# Download a single video as audio
result = downloader.download_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", audio_only=True)
if result:
    downloaded_file, video_info = result
    print(f"Downloaded to: {downloaded_file}")
    print(f"Title: {video_info['title']}")
    print(f"Views: {video_info['view_count']}")
```

### Managing Playlists

```python
from downloader.tracker import DownloadTracker

# Initialize the tracker
tracker = DownloadTracker()

# Add a playlist to track
tracker.add_playlist(
    url="https://www.youtube.com/playlist?list=PLexample123",
    name="My Favorite Songs",
    check_interval=12  # Check every 12 hours
)

# List all playlists
playlists = tracker.get_playlists()
for playlist in playlists:
    print(f"Name: {playlist['name']}")
    print(f"URL: {playlist['url']}")
    print(f"Last checked: {playlist['last_checked']}")
```

### Converting Audio Files

```python
from downloader.converter import AudioConverter

# Convert an audio file to MP3
mp3_file = AudioConverter.convert_to_mp3("input.wav", bitrate="320k")

# Normalize audio levels
normalized_file = AudioConverter.normalize_audio(mp3_file, target_level=-16.0)
```

### Working with the Scoring System

```python
from downloader.scoring import ScoringSystem

# Initialize the scoring system
scoring = ScoringSystem()

# Get the current time slot
current_slot = scoring.get_current_time_slot()
print(f"Current time slot: {current_slot}")

# Get top videos for current time slot
top_videos = scoring.get_top_videos(time_slot=current_slot, limit=10)
for i, video in enumerate(top_videos, 1):
    print(f"{i}. {video['title']} - Score: {video['score']:.2f}")
```