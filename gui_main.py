#!/usr/bin/env python3
"""
GUI Application for YouTube Playlist Downloader.
"""
import os
import sys
import logging
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import qdarkstyle

# Import custom modules
from utils.logger import setup_logging
from data.config_manager import ConfigHandler
from downloader.youtube import YouTubeDownloader
from downloader.tracker import DownloadTracker
from downloader.scoring import ScoringSystem
from audio.player import AudioPlayer
from gui.main_window import YouTubePlaylistDownloaderApp

def setup_data_directories():
    """Create necessary data directories."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="YouTube Playlist Downloader GUI - Download, manage, and play YouTube playlists"
    )
    
    # Configuration options
    parser.add_argument(
        "--config", "-c",
        default="config.ini",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Directory to save downloaded files"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the GUI application."""
    # Create necessary directories
    setup_data_directories()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(log_level=args.log_level, log_file="logs/app.log")
    logging.info("Starting YouTube Playlist Downloader GUI")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Playlist Downloader")
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    # Set application icon if available
    icon_path = os.path.join("gui", "icons", "logo.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Initialize main application window
    window = YouTubePlaylistDownloaderApp()
    window.show()
    
    # Override config settings if provided as arguments
    if args.output_dir:
        window.config.set("general", "output_directory", args.output_dir)
        # Recreate downloader with new output dir
        window.output_dir = args.output_dir
        window.downloader = YouTubeDownloader(window.output_dir, window.config)
        logging.info(f"Output directory set to: {args.output_dir}")
    
    # Run application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())