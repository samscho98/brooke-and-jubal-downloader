# CLI Module

A command-line interface module for YouTube playlist and video management.

## Overview

The `cli` module offers a comprehensive command-line interface for downloading, tracking, and managing YouTube videos and playlists. It includes functionality for downloading content, managing playlists, updating metadata, and displaying statistics.

## Classes and Functions

### CLIApp

`CLIApp` is the main application class that coordinates all command-line interface functionality.

#### Methods

- `__init__(config_path="config.ini")`: Initializes the CLI application.
  - `config_path`: Path to configuration file

- `parse_arguments()`: Parses command line arguments.
  - Returns: Parsed arguments (argparse.Namespace)

- `process_arguments(args)`: Processes command line arguments.
  - `args`: Parsed command line arguments
  - Returns: Exit code (int)

- `show_interactive_menu()`: Shows interactive menu for CLI operation.
  - Returns: Exit code (int)

- `run()`: Runs the CLI application.
  - Returns: Exit code (int)

### Command Functions

- `download_command(downloader, tracker, url)`: Downloads a YouTube video or playlist.
  - `downloader`: YouTubeDownloader instance
  - `tracker`: DownloadTracker instance
  - `url`: YouTube URL to download
  - Returns: Exit code (int)

- `add_playlist_command(tracker, url)`: Adds a playlist to track.
  - `tracker`: DownloadTracker instance
  - `url`: YouTube playlist URL
  - Returns: Exit code (int)

- `list_playlists_command(tracker)`: Lists all tracked playlists.
  - `tracker`: DownloadTracker instance
  - Returns: Exit code (int)

- `update_playlists_command(tracker, downloader, config)`: Updates all playlists that need updating.
  - `tracker`: DownloadTracker instance
  - `downloader`: YouTubeDownloader instance
  - `config`: ConfigHandler instance
  - Returns: Exit code (int)

- `remove_playlist_command(tracker, url)`: Removes a playlist from tracking.
  - `tracker`: DownloadTracker instance
  - `url`: YouTube playlist URL
  - Returns: Exit code (int)

- `update_view_counts_command(tracker, downloader)`: Updates view counts for all downloaded videos.
  - `tracker`: DownloadTracker instance
  - `downloader`: YouTubeDownloader instance
  - Returns: Exit code (int)

- `display_video_stats_command(tracker)`: Displays statistics about downloaded videos.
  - `tracker`: DownloadTracker instance
  - Returns: Exit code (int)

- `display_top_videos_command(tracker, limit=10)`: Displays top videos by view count.
  - `tracker`: DownloadTracker instance
  - `limit`: Number of videos to display
  - Returns: Exit code (int)

- `display_top_scored_videos_command(scoring, limit=10)`: Displays top videos by score.
  - `scoring`: ScoreCalculator instance
  - `limit`: Number of videos to display
  - Returns: Exit code (int)

### Display Utilities

- `setup_logging(log_level="INFO", log_file=None)`: Sets up logging configuration.
  - `log_level`: Logging level
  - `log_file`: Optional file to log to

- `format_date(date_str, input_format="%Y%m%d", output_format="%B %d, %Y")`: Formats a date string.
  - `date_str`: Date string to format
  - `input_format`: Input date format
  - `output_format`: Output date format
  - Returns: Formatted date string or original string if formatting fails

- `format_size(size_bytes)`: Formats a file size to a human-readable string.
  - `size_bytes`: Size in bytes
  - Returns: Human-readable size string

- `format_duration(duration_seconds)`: Formats a duration to a human-readable string.
  - `duration_seconds`: Duration in seconds
  - Returns: Human-readable duration string

- `print_header(text, char="=", width=80)`: Prints a header with the given text.
  - `text`: Header text
  - `char`: Character to use for the separator line
  - `width`: Width of the separator line

- `print_list_item(index, title, details=None, indent=3)`: Prints a list item with details.
  - `index`: Item index
  - `title`: Item title
  - `details`: Optional dictionary of key-value details
  - `indent`: Indentation for details

- `confirm_action(prompt, default=False)`: Asks for confirmation before proceeding with an action.
  - `prompt`: Prompt to display
  - `default`: Default answer if user just presses Enter
  - Returns: Boolean indicating if action was confirmed

## Usage

The CLI module provides both command-line argument-based operation and an interactive menu system:

### Command-Line Arguments

```
python -m cli.app --download URL        # Download a video or playlist
python -m cli.app --add-playlist URL    # Add a playlist to track
python -m cli.app --list-playlists      # List all tracked playlists
python -m cli.app --update-all          # Update all playlists
python -m cli.app --stats               # Display video statistics
```

### Interactive Menu

Running the application without arguments (`python -m cli.app`) will display an interactive menu with the following options:

1. Download a video/playlist
2. Add a playlist to track
3. List tracked playlists
4. Update all tracked playlists
5. Remove a playlist
6. Update view counts for all videos
7. Show video statistics
8. Show top videos by view count
9. Show top videos by score
10. Exit