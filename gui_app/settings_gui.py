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
        self.root.title("YouTube Playlist Downloader - Settings")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Initialize configuration and trackers
        self.config = ConfigHandler("config.ini")
        self.tracker = DownloadTracker()
        self.output_dir = self.config.get("general", "output_directory")
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs with component panels
        self.playlists_tab = PlaylistPanel(self.notebook, self.tracker)
        self.settings_tab = SettingsPanel(self.notebook, self.config)
        self.about_tab = self._create_about_tab()
        
        self.notebook.add(self.playlists_tab, text="Playlists")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.about_tab, text="About")
        
        # Create action buttons at the bottom
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
A Python application that downloads videos from YouTube playlists as MP3 files 
and keeps track of downloaded files to ensure your collection stays up to date.

This GUI is for managing the settings and playlists. 
Use the 'Run Downloader (Console)' button to launch the main application.
        """
        desc_label = ttk.Label(about_frame, text=description, justify="center", wraplength=500)
        desc_label.pack(pady=10)
        
        # Features
        features = """
Features:
• Download individual YouTube videos as MP3 files
• Download entire YouTube playlists as MP3 files
• Track playlists to check for new videos at configurable intervals
• Maintain a history of downloaded videos to avoid duplicates
• Convert downloaded audio to different formats if needed
        """
        features_label = ttk.Label(about_frame, text=features, justify="left", wraplength=500)
        features_label.pack(pady=10)
        
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