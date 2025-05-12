#!/usr/bin/env python3
"""
Main CLI application module for YouTube Playlist Downloader.
"""
import os
import sys
import logging
from typing import List, Optional
import time
import argparse

from data.config_manager import ConfigHandler
from data.file_manager import FileManager
from downloader.youtube import YouTubeDownloader
from downloader.converter import AudioConverter
from downloader.tracker import DownloadTracker
from cli.commands import (
    download_command, 
    add_playlist_command, 
    list_playlists_command,
    update_playlists_command,
    remove_playlist_command,
    update_view_counts_command,
    display_video_stats_command,
    display_top_videos_command,
    display_top_scored_videos_command
)
from cli.display import setup_logging

class CLIApp:
    """Command-line interface application."""
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize the CLI application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = ConfigHandler(config_path)
        
        # Set up output directory
        self.output_dir = self.config.get("general", "output_directory")
        
        # Initialize components
        self.file_manager = FileManager(self.output_dir)
        self.downloader = YouTubeDownloader(self.output_dir, self.config)
        self.converter = AudioConverter()
        
        # Initialize tracker with correct paths in the new structure
        self.tracker = DownloadTracker(
            history_file="data/download_history.json",
            playlists_file="data/playlists.json"
        )
        
        # Setup logging
        log_level = self.config.get("logging", "level", "INFO")
        log_file = self.config.get("logging", "file", None)
        log_to_console = self.config.getboolean("logging", "console", True)
        
        setup_logging(
            log_level=log_level,
            log_file=log_file if log_to_console else None
        )
        
        logging.info(f"Initialized CLI application with config file: {config_path}")
    
    def parse_arguments(self) -> argparse.Namespace:
        """
        Parse command line arguments.
        
        Returns:
            Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description="YouTube Playlist Downloader - Download videos as audio files"
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

        parser.add_argument(
            "--top-scored",
            metavar="N",
            type=int,
            help="Show top N videos by score"
        )
        
        parser.add_argument(
            "--update-views",
            action="store_true",
            help="Update view counts for all downloaded videos"
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show statistics about downloaded videos"
        )
        parser.add_argument(
            "--top-views",
            metavar="N",
            type=int,
            help="Show top N videos by view count"
        )
        
        # Configuration arguments
        parser.add_argument(
            "--config", "-c",
            metavar="FILE",
            default=self.config_path,
            help=f"Path to configuration file (default: {self.config_path})"
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
            help="Set logging level"
        )
        parser.add_argument(
            "--log-file",
            metavar="FILE",
            help="File to log to (in addition to console)"
        )
        
        return parser.parse_args()
    
    def process_arguments(self, args: argparse.Namespace) -> int:
        """
        Process command line arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code
        """
        # Override config with command line arguments if provided
        if args.output_dir:
            self.config.set("general", "output_directory", args.output_dir)
            # Recreate downloader with new output dir
            self.output_dir = args.output_dir
            self.downloader = YouTubeDownloader(self.output_dir, self.config)
            
        if args.check_interval:
            self.config.set("general", "check_interval", str(args.check_interval))
        
        # Update logging if specified
        if args.log_level or args.log_file:
            log_level = args.log_level or self.config.get("logging", "level", "INFO")
            log_file = args.log_file or self.config.get("logging", "file", None)
            log_to_console = self.config.getboolean("logging", "console", True)
            
            setup_logging(
                log_level=log_level,
                log_file=log_file if log_to_console else None
            )
            
            logging.info(f"Updated logging: level={log_level}, file={log_file}")
        
        # Save any config changes
        self.config.save_config()
        
        # Process command line arguments
        if args.add_playlist:
            return add_playlist_command(self.tracker, args.add_playlist)
        
        elif args.list_playlists:
            return list_playlists_command(self.tracker)

        elif args.top_scored:
            limit = max(1, args.top_scored)
            # Try to import scoring system here, to avoid errors if it's not implemented yet
            try:
                from scoring.score_calculator import ScoreCalculator
                scoring_system = ScoreCalculator()
                return display_top_scored_videos_command(scoring_system, limit)
            except ImportError:
                print("Scoring system not implemented yet.")
                return 1
        
        elif args.remove_playlist:
            return remove_playlist_command(self.tracker, args.remove_playlist)
        
        elif args.download:
            return download_command(self.downloader, self.tracker, args.download)
        
        elif args.update_views:
            return update_view_counts_command(self.tracker, self.downloader)
        
        elif args.stats:
            return display_video_stats_command(self.tracker)
        
        elif args.top_views:
            limit = max(1, args.top_views)
            return display_top_videos_command(self.tracker, limit)
        
        elif args.update_all:
            return update_playlists_command(self.tracker, self.downloader, self.config)
        
        else:
            # If no specific action, show interactive menu
            return self.show_interactive_menu()
    
    def show_interactive_menu(self) -> int:
        """
        Show interactive menu for CLI operation.
        
        Returns:
            Exit code
        """
        while True:
            print("\nYouTube Playlist Downloader")
            print("==========================")
            print("1. Download a video/playlist")
            print("2. Add a playlist to track")
            print("3. List tracked playlists")
            print("4. Update all tracked playlists")
            print("5. Remove a playlist")
            print("6. Update view counts for all videos")
            print("7. Show video statistics")
            print("8. Show top videos by view count")
            print("9. Show top videos by score")
            print("10. Exit")
            
            choice = input("\nEnter your choice (1-10): ")
            
            if choice == "1":
                url = input("Enter YouTube URL: ")
                if not url:
                    print("URL is required")
                    continue
                    
                download_command(self.downloader, self.tracker, url)
            
            elif choice == "2":
                url = input("Enter playlist URL: ")
                if not url:
                    print("URL is required")
                    continue
                    
                add_playlist_command(self.tracker, url)
            
            elif choice == "3":
                list_playlists_command(self.tracker)
            
            elif choice == "4":
                update_playlists_command(self.tracker, self.downloader, self.config)
            
            elif choice == "5":
                display_playlists = list_playlists_command(self.tracker)
                index = input("\nEnter the number of the playlist to remove: ")
                
                try:
                    index = int(index) - 1
                    playlists = self.tracker.get_playlists()
                    
                    if 0 <= index < len(playlists):
                        url = playlists[index]["url"]
                        remove_playlist_command(self.tracker, url)
                    else:
                        print("Invalid playlist number")
                        
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            elif choice == "6":
                update_view_counts_command(self.tracker, self.downloader)
                
            elif choice == "7":
                display_video_stats_command(self.tracker)
                
            elif choice == "8":
                limit_input = input("How many videos to show? (default: 10): ")
                try:
                    limit = int(limit_input) if limit_input.strip() else 10
                    display_top_videos_command(self.tracker, limit)
                except ValueError:
                    print("Invalid input. Showing top 10 videos.")
                    display_top_videos_command(self.tracker, 10)
            
            elif choice == "9":
                limit_input = input("How many videos to show? (default: 10): ")
                try:
                    limit = int(limit_input) if limit_input.strip() else 10
                    # Try to import scoring system here
                    try:
                        from scoring.score_calculator import ScoreCalculator
                        scoring_system = ScoreCalculator()
                        display_top_scored_videos_command(scoring_system, limit)
                    except ImportError:
                        print("Scoring system not implemented yet.")
                except ValueError:
                    print("Invalid input. Showing top 10 videos.")
                    try:
                        from scoring.score_calculator import ScoreCalculator
                        scoring_system = ScoreCalculator()
                        display_top_scored_videos_command(scoring_system, 10)
                    except ImportError:
                        print("Scoring system not implemented yet.")
            
            elif choice == "10":
                print("Exiting...")
                return 0
            
            else:
                print("Invalid choice. Please try again.")
            
            # Small pause before showing the menu again
            time.sleep(1)
    
    def run(self) -> int:
        """
        Run the CLI application.
        
        Returns:
            Exit code
        """
        args = self.parse_arguments()
        return self.process_arguments(args)