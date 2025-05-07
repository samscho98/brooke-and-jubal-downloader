#!/usr/bin/env python3
"""
YouTube Playlist Downloader Application.
Downloads videos from YouTube playlists as MP3 files and keeps track of the collection.
"""

# Import necessary modules
import os
import sys
import logging
import argparse
from typing import List, Optional
import time

from utils.config_handler import ConfigHandler
from utils.file_manager import FileManager
from downloader.youtube import YouTubeDownloader
from downloader.converter import AudioConverter
from downloader.tracker import DownloadTracker

# Set up logging
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional file to log to
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers
    )

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="YouTube Playlist Downloader - Download videos as MP3 files"
    )
    
    # Core functionality arguments
    parser.add_argument(
        "--download", "-d",
        metavar="URL",
        help="Download a YouTube video or playlist"
    )
    parser.add_argument(
        "--add-playlist", "-a",
        metavar="URL",
        help="Add a playlist to track"
    )
    parser.add_argument(
        "--list-playlists", "-l",
        action="store_true",
        help="List all tracked playlists"
    )
    parser.add_argument(
        "--update-all", "-u",
        action="store_true",
        help="Update all tracked playlists"
    )
    parser.add_argument(
        "--remove-playlist", "-r",
        metavar="URL",
        help="Remove a playlist from tracking"
    )
    
    # Configuration arguments
    parser.add_argument(
        "--config", "-c",
        metavar="FILE",
        default="config.ini",
        help="Path to configuration file (default: config.ini)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        metavar="DIR",
        help="Directory to save downloaded files"
    )
    parser.add_argument(
        "--check-interval",
        metavar="HOURS",
        type=int,
        help="How often to check for updates (in hours)"
    )
    
    # Logging arguments
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level"
    )
    parser.add_argument(
        "--log-file",
        metavar="FILE",
        help="File to log to (in addition to console)"
    )
    
    return parser.parse_args()

# Update the display_playlists function in main.py to handle None values properly

def display_playlists(tracker: DownloadTracker) -> None:
    """
    Display all tracked playlists.
    
    Args:
        tracker: Download tracker instance
    """
    playlists = tracker.get_playlists()
    
    if not playlists:
        print("No playlists are currently being tracked")
        return
    
    print(f"\nTracked Playlists ({len(playlists)}):")
    print("-" * 80)
    for i, playlist in enumerate(playlists, 1):
        name = playlist.get("name", "Unnamed Playlist")
        url = playlist.get("url", "N/A")
        interval = playlist.get("check_interval", 24)
        last_checked = playlist.get("last_checked", "Never")
        
        # Fix: Check if last_checked is None or "Never" before trying to convert it
        if last_checked is not None and last_checked != "Never":
            from datetime import datetime
            try:
                last_checked = datetime.fromisoformat(last_checked).strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid date format for playlist {name}: {e}")
                last_checked = str(last_checked)
        
        print(f"{i}. {name}")
        print(f"   URL: {url}")
        print(f"   Check Interval: {interval} hours")
        print(f"   Last Checked: {last_checked}")
        print()

def update_playlists(tracker: DownloadTracker, downloader: YouTubeDownloader, config: ConfigHandler) -> None:
    """
    Update all playlists that need updating based on their check interval.
    
    Args:
        tracker: Download tracker instance
        downloader: YouTube downloader instance
        config: Configuration handler instance
    """
    playlists_to_update = tracker.check_for_updates()
    
    if not playlists_to_update:
        print("No playlists need updating at this time")
        return
    
    print(f"Updating {len(playlists_to_update)} playlists...")
    
    # Get audio settings from config
    audio_format = config.get("audio", "format", "mp3")
    audio_bitrate = config.get("audio", "bitrate", "192k")
    normalize_audio = config.getboolean("audio", "normalize_audio", False)
    target_level = config.getfloat("audio", "target_level", -18.0)
    
    for playlist in playlists_to_update:
        url = playlist.get("url")
        name = playlist.get("name", "Unnamed Playlist")
        
        print(f"\nProcessing playlist: {name}")
        print(f"URL: {url}")
        
        # Get videos in the playlist
        videos = downloader.get_playlist_videos(url)
        
        if not videos:
            print("No videos found in playlist or error retrieving playlist")
            continue
        
        print(f"Found {len(videos)} videos in playlist")
        
        # Check which videos have already been downloaded
        new_videos = [v for v in videos if not tracker.is_video_downloaded(v['id'])]
        
        if not new_videos:
            print("All videos have already been downloaded")
            # Update the last checked time even if no new videos
            tracker.update_playlist_check_time(url)
            continue
        else:
            print(f"Found {len(new_videos)} new videos to download...")
            
            for i, video in enumerate(new_videos, 1):
                print(f"  [{i}/{len(new_videos)}] Downloading: {video['title']}")
                
                # Extract playlist ID from URL
                import re
                playlist_id_match = re.search(r'list=([^&]+)', url)
                playlist_id = playlist_id_match.group(1) if playlist_id_match else "unknown"
                
                # Download the video
                file_path = downloader.download_video(video['url'], audio_only=True, playlist_name=name)
                
                if file_path:
                    # Check if we need to convert the file format
                    file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                    if file_ext != audio_format:
                        from downloader.converter import AudioConverter
                        print(f"    Converting to {audio_format} format...")
                        converted_file = AudioConverter.convert_audio(
                            file_path, 
                            audio_format, 
                            bitrate=audio_bitrate
                        )
                        if converted_file:
                            # Remove the original file if conversion was successful
                            if os.path.exists(file_path) and file_path != converted_file:
                                os.remove(file_path)
                            file_path = converted_file
                    
                    # Add to download history
                    tracker.add_downloaded_video(
                        video_id=video['id'],
                        playlist_id=playlist_id,
                        title=video['title'],
                        file_path=file_path
                    )
                    print(f"    ✓ Downloaded to: {file_path}")
                else:
                    print(f"    ✗ Failed to download")
        
        # Update the last checked time
        tracker.update_playlist_check_time(url)

def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        Exit code
    """
    args = parse_arguments()
    
    # Load configuration
    config = ConfigHandler(args.config)
    
    # Override with command line arguments if provided
    if args.output_dir:
        config.set("general", "output_directory", args.output_dir)
    if args.check_interval:
        config.set("general", "check_interval", str(args.check_interval))
    
    # Get logging settings from config, but command line args take precedence
    log_level = args.log_level if args.log_level else config.get("logging", "level", "INFO")
    log_file = args.log_file if args.log_file else config.get("logging", "file", None)
    log_to_console = config.getboolean("logging", "console", True)
    
    # Set up logging with the determined settings
    setup_logging(
        log_level=log_level,
        log_file=log_file if log_to_console else None
    )
    
    # Now log some diagnostic information
    logging.info(f"Starting application with config file: {args.config}")
    logging.info(f"Log level: {log_level}")
    logging.info(f"Log file: {log_file}")
    
    config.save_config()
    
    # Initialize components
    output_dir = config.get("general", "output_directory")
    file_manager = FileManager(output_dir)
    downloader = YouTubeDownloader(output_dir, config)
    converter = AudioConverter()
    tracker = DownloadTracker(
        history_file="gui_app/download_history.json",
        playlists_file="gui_app/playlists.json"
    )
    
    # Process command line arguments
    if args.add_playlist:
        name = input("Enter a name for this playlist: ")
        interval = input("Check interval in hours (default: 24): ")
        
        if not interval.strip():
            interval = "24"
            
        try:
            interval = int(interval)
            success = tracker.add_playlist(
                url=args.add_playlist,
                name=name,
                check_interval=interval
            )
            
            if success:
                print(f"Successfully added playlist: {name}")
            else:
                print("Failed to add playlist")
                
        except ValueError:
            print("Invalid check interval. Using default: 24 hours")
            success = tracker.add_playlist(
                url=args.add_playlist,
                name=name
            )
            if success:
                print(f"Successfully added playlist: {name}")
            else:
                print("Failed to add playlist")
    
    elif args.list_playlists:
        display_playlists(tracker)
    
    elif args.remove_playlist:
        success = tracker.remove_playlist(args.remove_playlist)
        if success:
            print(f"Successfully removed playlist: {args.remove_playlist}")
        else:
            print(f"Failed to remove playlist: {args.remove_playlist}")
    
    elif args.download:
        url = args.download
        print(f"Downloading: {url}")
        
        if "list=" in url:  # It's a playlist
            print("Detected playlist URL")
            successful, failed = downloader.download_playlist(url, audio_only=True)
            
            print(f"\nDownloaded {len(successful)} videos, {len(failed)} failed")
            if failed:
                print("Failed videos:")
                for video_id in failed:
                    print(f"  - {video_id}")
        else:  # It's a single video
            print("Detected single video URL")
            result = downloader.download_video(url, audio_only=True)
            
            if result:
                print(f"Successfully downloaded to: {result}")
            else:
                print("Failed to download video")
    
    elif args.update_all:
        update_playlists(tracker, downloader, config)
    
    else:
        # If no specific action, show menu
        while True:
            print("\nYouTube Playlist Downloader")
            print("==========================")
            print("1. Download a video/playlist")
            print("2. Add a playlist to track")
            print("3. List tracked playlists")
            print("4. Update all tracked playlists")
            print("5. Remove a playlist")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                url = input("Enter YouTube URL: ")
                print(f"Downloading: {url}")
                
                if "list=" in url:  # It's a playlist
                    print("Detected playlist URL")
                    # Try to get playlist name 
                    playlist_name = None
                    for playlist in tracker.get_playlists():
                        if playlist["url"] == url:
                            playlist_name = playlist["name"]
                            break
                            
                    if not playlist_name:
                        playlist_name = input("Enter a name for this playlist (for folder organization): ")
                        
                    successful, failed = downloader.download_playlist(url, audio_only=True, playlist_name=playlist_name)
                    
                    print(f"\nDownloaded {len(successful)} videos, {len(failed)} failed")
                else:  # It's a single video
                    print("Detected single video URL")
                    result = downloader.download_video(url, audio_only=True)
                    
                    if result:
                        print(f"Successfully downloaded to: {result}")
                    else:
                        print("Failed to download video")
            
            elif choice == "2":
                url = input("Enter playlist URL: ")
                name = input("Enter a name for this playlist: ")
                interval = input("Check interval in hours (default: 24): ")
                
                if not interval.strip():
                    interval = "24"
                    
                try:
                    interval = int(interval)
                    success = tracker.add_playlist(
                        url=url,
                        name=name,
                        check_interval=interval
                    )
                    
                    if success:
                        print(f"Successfully added playlist: {name}")
                    else:
                        print("Failed to add playlist")
                        
                except ValueError:
                    print("Invalid check interval. Using default: 24 hours")
                    success = tracker.add_playlist(
                        url=url,
                        name=name
                    )
                    if success:
                        print(f"Successfully added playlist: {name}")
                    else:
                        print("Failed to add playlist")
            
            elif choice == "3":
                display_playlists(tracker)
            
            elif choice == "4":
                update_playlists(tracker, downloader, config)
            
            elif choice == "5":
                display_playlists(tracker)
                index = input("\nEnter the number of the playlist to remove: ")
                
                try:
                    index = int(index) - 1
                    playlists = tracker.get_playlists()
                    
                    if 0 <= index < len(playlists):
                        url = playlists[index]["url"]
                        success = tracker.remove_playlist(url)
                        
                        if success:
                            print(f"Successfully removed playlist")
                        else:
                            print("Failed to remove playlist")
                    else:
                        print("Invalid playlist number")
                        
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            elif choice == "6":
                print("Exiting...")
                return 0
            
            else:
                print("Invalid choice. Please try again.")
            
            # Small pause before showing the menu again
            time.sleep(1)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.exception("Unhandled exception")
        print(f"\nError: {str(e)}")
        sys.exit(1)