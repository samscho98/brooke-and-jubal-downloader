#!/usr/bin/env python3
"""
Settings GUI for YouTube Playlist Downloader
A simple graphical interface to manage settings and playlists
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
from datetime import datetime
import traceback
import threading

# Add parent directory to path to allow imports from main project
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.config_handler import ConfigHandler
from downloader.tracker import DownloadTracker
from downloader.youtube import YouTubeDownloader

# Import GUI components directly from their modules to avoid circular imports
from gui_app.components.playlist_manager import PlaylistPanel
from gui_app.components.settings_panel import SettingsPanel

class PlaylistDownloaderGUI:
    """GUI application for managing YouTube Playlist Downloader settings"""
    
    def __init__(self, root):
        """Initialize the GUI application"""
        self.root = root
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("950x650")
        self.root.minsize(900, 600)
        
        # Initialize configuration and trackers
        self.config = ConfigHandler("config.ini")
        self.tracker = DownloadTracker(
                history_file="gui_app/download_history.json",
                playlists_file="gui_app/playlists.json"
            )
        self.output_dir = self.config.get("general", "output_directory")
        self.downloader = YouTubeDownloader(self.output_dir, self.config)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs) at the top
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs with component panels
        self.playlists_tab = PlaylistPanel(self.notebook, self.tracker)
        self.single_video_tab = self._create_single_video_tab()
        self.settings_tab = SettingsPanel(self.notebook, self.config)
        self.about_tab = self._create_about_tab()
        
        self.notebook.add(self.playlists_tab, text="Playlists")
        self.notebook.add(self.single_video_tab, text="Download Video")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.about_tab, text="About")
        
        # Create button frame at the bottom
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Add run console app button
        self.run_button = ttk.Button(
            self.button_frame, 
            text="Run Downloader (Console)", 
            command=self._run_console_app
        )
        self.run_button.pack(side=tk.RIGHT, padx=5)
        
        # Add save settings button
        self.save_button = ttk.Button(
            self.button_frame, 
            text="Save Settings", 
            command=self._save_settings
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
    def _create_single_video_tab(self):
        """Create the single video download tab"""
        video_frame = ttk.Frame(self.notebook, padding="20")
        
        # Title
        title_label = ttk.Label(
            video_frame, 
            text="Download Single YouTube Video", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Input frame
        input_frame = ttk.Frame(video_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Video URL entry
        ttk.Label(input_frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.video_url_var = tk.StringVar()
        url_entry = ttk.Entry(input_frame, textvariable=self.video_url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Audio format selection
        ttk.Label(input_frame, text="Audio Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.video_format_var = tk.StringVar(value=self.config.get("audio", "format", "mp3"))
        format_combo = ttk.Combobox(input_frame, textvariable=self.video_format_var, 
                                   values=["mp3", "wav", "m4a", "ogg"], width=10)
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Download button
        download_button = ttk.Button(
            video_frame,
            text="Download Video",
            command=self._download_single_video,
            width=20
        )
        download_button.pack(pady=20)
        
        # Status frame
        status_frame = ttk.LabelFrame(video_frame, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.video_status_var = tk.StringVar(value="Ready to download")
        status_label = ttk.Label(status_frame, textvariable=self.video_status_var, padding=10)
        status_label.pack(fill=tk.X)
        
        # Instructions
        instructions = """
Enter a YouTube video URL above and click "Download Video" to download it as an audio file.
The audio will be saved in the output directory specified in Settings.

Supported formats: MP3, WAV, M4A, OGG
        """
        instructions_label = ttk.Label(video_frame, text=instructions, justify=tk.LEFT, wraplength=500)
        instructions_label.pack(pady=20, anchor=tk.W)
        
        # Configure grid to expand with window
        input_frame.columnconfigure(1, weight=1)
        
        return video_frame
        
    def _create_about_tab(self):
        """Create the About tab"""
        about_frame = ttk.Frame(self.notebook, padding="20")
        
        # App title
        title_label = ttk.Label(
            about_frame, 
            text="YouTube Playlist Downloader", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Description
        description = """
    A Python application that downloads videos from YouTube playlists as audio files 
    and keeps track of downloaded files to ensure your collection stays up to date.

    This GUI is for managing the settings and playlists. 
    Use the 'Run Downloader (Console)' button to launch the main application.
        """
        desc_label = ttk.Label(about_frame, text=description, justify="center", wraplength=500)
        desc_label.pack(pady=10)
        
        # Features
        features = """
    Features:
    - Download individual YouTube videos as audio files in multiple formats (MP3, WAV, OGG, M4A)
    - Download entire YouTube playlists with automatic organization into folders
    - Track playlists to check for new videos at configurable intervals
    - Maintain a history of downloaded videos to avoid duplicates
    - Convert downloaded audio to different formats with customizable bitrate
    - Normalize audio levels for consistent volume across tracks
    - Easy-to-use GUI for managing playlists and settings
    - Powerful command-line interface for automation
        """
        features_label = ttk.Label(about_frame, text=features, justify="left", wraplength=500)
        features_label.pack(pady=10)
        
        # Created for
        created_for_label = ttk.Label(
            about_frame,
            text="Created for:",
            font=("Arial", 10, "bold")
        )
        created_for_label.pack(pady=(10, 0))
        
        tiktok_link = "https://www.tiktok.com/@respawnandride"
        tiktok_label = ttk.Label(
            about_frame,
            text=tiktok_link,
            foreground="blue",
            cursor="hand2"
        )
        tiktok_label.pack(pady=(0, 5))
        tiktok_label.bind("<Button-1>", lambda e: self._open_url(tiktok_link))
        
        # Developer info
        developer_label = ttk.Label(
            about_frame,
            text="Developer:",
            font=("Arial", 10, "bold")
        )
        developer_label.pack(pady=(10, 0))
        
        github_link = "https://github.com/samscho98"
        github_label = ttk.Label(
            about_frame,
            text=github_link,
            foreground="blue",
            cursor="hand2"
        )
        github_label.pack(pady=(0, 5))
        github_label.bind("<Button-1>", lambda e: self._open_url(github_link))
        
        # Version and copyright
        version_label = ttk.Label(
            about_frame, 
            text="Version 1.0.0", 
            font=("Arial", 10)
        )
        version_label.pack(pady=5)
        
        copyright_label = ttk.Label(
            about_frame, 
            text="Copyright © 2025", 
            font=("Arial", 10)
        )
        copyright_label.pack(pady=5)
        
        return about_frame

    def _open_url(self, url):
        """Open a URL in the default web browser"""
        import webbrowser
        webbrowser.open(url)
    
    def _download_single_video(self):
        """Download a single YouTube video with improved logging"""
        url = self.video_url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube video URL")
            return
            
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        # Get the logger
        import logging
        logger = logging.getLogger(__name__)
        
        # Configure the root logger if not already configured
        if not logging.getLogger().handlers:
            log_level = self.config.get("logging", "level", "INFO")
            log_file = self.config.get("logging", "file", "app.log")
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
            # Set numeric level
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            
            # Create handlers
            handlers = []
            if log_file:
                try:
                    handlers.append(logging.FileHandler(log_file))
                    logger.info(f"Log file set to: {log_file}")
                except Exception as e:
                    logger.error(f"Could not create log file handler: {str(e)}")
            
            # Add console handler
            if self.config.getboolean("logging", "console", True):
                handlers.append(logging.StreamHandler())
            
            # Configure logging
            logging.basicConfig(
                level=numeric_level,
                format=log_format,
                handlers=handlers
            )
        
        # Log the start of the download
        logger.info(f"Starting download for video: {url}")
        self.video_status_var.set("Downloading video...")
        
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", f"Download video:\n{url}?"):
            logger.info("Download cancelled by user")
            self.video_status_var.set("Download cancelled")
            return
            
        # Get audio format from settings
        audio_format = self.video_format_var.get()
        logger.info(f"Selected audio format: {audio_format}")
        
        def download_thread():
            try:
                # Update the format in config
                self.config.set("audio", "format", audio_format)
                logger.info(f"Updating config with format: {audio_format}")
                
                # Set log level to DEBUG temporarily for more detailed logs
                previous_level = logging.getLogger().level
                logging.getLogger().setLevel(logging.DEBUG)
                
                # Log thread start
                logger.debug(f"Download thread started for URL: {url}")
                
                # Run the download
                logger.info(f"Starting download using YouTubeDownloader for URL: {url}")
                result = self.downloader.download_video(url, audio_only=True)
                
                # Restore previous log level
                logging.getLogger().setLevel(previous_level)
                
                # Update UI in the main thread
                self.root.after(100, lambda: self._update_download_status(result))
                
            except Exception as e:
                # Log the error
                logger.error(f"Error during download: {str(e)}", exc_info=True)
                
                # Restore previous log level
                logging.getLogger().setLevel(previous_level)
                
                # Update UI in the main thread
                error_msg = str(e)
                self.root.after(100, lambda: self._update_download_status(None, error_msg))
            
        # Start the download thread
        import threading
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        logger.info("Download thread launched")
        
    def _update_download_status(self, result, error=None):
        """Update the UI after a download completes with improved logging"""
        import logging
        logger = logging.getLogger(__name__)
        
        if result:
            logger.info(f"Download completed successfully: {result}")
            self.video_status_var.set("Download completed")
            messagebox.showinfo("Success", f"Video downloaded to:\n{result}")
            self.video_url_var.set("")  # Clear the URL field
        else:
            logger.error(f"Download failed: {error or 'Unknown error'}")
            self.video_status_var.set("Download failed")
            
            # Create a more detailed error message
            error_details = f"Failed to download video: {error or 'Unknown error'}"
            logger.error(error_details)
            
            # Log file location for user reference
            log_file = self.config.get("logging", "file", "app.log")
            error_message = f"{error_details}\n\nMore details can be found in the log file: {log_file}"
            
            messagebox.showerror("Error", error_message)
        
    def _save_settings(self):
        """Save settings to config file"""
        try:
            # Save settings panel
            if self.settings_tab.save_settings():
                messagebox.showinfo("Success", "Settings saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save settings")
                
        except Exception as e:
            # Print the full traceback to help with debugging
            print(f"Error saving settings: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
            
    def _run_console_app(self, extra_args=None):
        """Run the console application"""
        # Get the path to the main.py script
        main_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        if not os.path.exists(main_script):
            messagebox.showerror("Error", f"Could not find main script: {main_script}")
            return
            
        # Build command
        cmd = [sys.executable, main_script]
        
        # Add configuration path
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "config.ini")
        if os.path.exists(config_path):
            cmd.extend(["--config", config_path])
        
        # Add output directory from config
        output_dir = self.config.get("general", "output_directory")
        if output_dir:
            cmd.extend(["--output-dir", output_dir])
        
        # Add logging parameters from config
        log_level = self.config.get("logging", "level", "INFO")
        if log_level:
            cmd.extend(["--log-level", log_level])
        
        log_file = self.config.get("logging", "file")
        if log_file and self.config.getboolean("logging", "console", True):
            cmd.extend(["--log-file", log_file])
        
        # Add any additional arguments
        if extra_args:
            cmd.extend(extra_args)
        
        try:
            # Open a new console window to run the application
            if sys.platform == "win32":
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # For non-Windows platforms, just run without a new console
                subprocess.Popen(cmd)
                
            messagebox.showinfo("Success", "YouTube Playlist Downloader launched")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch downloader: {str(e)}")

def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()
    app = PlaylistDownloaderGUI(root)
    
    # Set window icon if available
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()