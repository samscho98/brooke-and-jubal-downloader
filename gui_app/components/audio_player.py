"""
Audio Player Component for YouTube Playlist Downloader
Allows playback of downloaded audio files with playlist selection
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Make sure parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class AudioPlayerPanel(ttk.Frame):
    """
    Panel for playing downloaded audio files
    
    This component provides a media player interface that allows:
    - Selecting which playlists to include in playback
    - Building a playback queue of audio tracks
    - Basic playback controls (play, pause, skip)
    - Volume adjustment
    
    The player reads from the download history JSON file to find
    available audio files and organizes them by playlist.
    """
    
    def __init__(self, parent, history_file: str = "gui_app/download_history.json"):
        """
        Initialize the audio player panel
        
        Args:
            parent: Parent widget
            history_file: Path to the download history file
        """
        super().__init__(parent)
        
        # Add detailed logging
        print("\n=== AudioPlayerPanel Initialization ===")
        print(f"Original history_file path: {history_file}")
        
        # Fix path issues with improved logging
        self.history_file = self._fix_path(history_file)
        print(f"Using history_file: {self.history_file}")
        
        # Rest of your init code remains unchanged
        self.current_track = None
        self.is_playing = False
        self.current_volume = 70  # Default volume (0-100)
        self.playlists = {}  # Dictionary of playlist name -> list of tracks
        self.selected_playlists = set()  # Set of selected playlist names
        self.playlist_queue = []  # Queue of tracks to play
        self.track_history = []  # History of played tracks
        
        # Initialize variables for UI elements
        self.selection_info_var = tk.StringVar(value="No playlists selected")
        self.track_title_var = tk.StringVar(value="No track selected")
        self.playlist_name_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Player ready")
        self.volume_var = tk.IntVar(value=self.current_volume)
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        
        # Create widgets first so status updates can be displayed
        self._create_widgets()
        
        # Then load history
        self.status_var.set("Loading download history...")
        self._load_download_history()
        
        # Start playback monitoring thread
        self.playback_thread = threading.Thread(target=self._monitor_playback, daemon=True)
        self.playback_thread.start()
        
    def _fix_path(self, path):
        """
        Fix file paths to handle different ways the app might be run.
        Tries multiple path variations to find the file.
        
        Args:
            path: Original path
            
        Returns:
            Working path or original if no better option found
        """
        print(f"\n_fix_path called for: {path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Parent directory: {parent_dir}")
        
        # List of possible path patterns to try
        possible_paths = [
            path,                                 # Original path
            os.path.join(os.getcwd(), path),      # Absolute from current dir
            path.replace('/', os.sep),            # Fix path separators
            os.path.basename(path),               # Just the filename in current dir
            os.path.join("gui_app", os.path.basename(path)),  # In gui_app subfolder
            os.path.join(parent_dir, path),       # Relative to parent dir 
            os.path.join(parent_dir, "gui_app", os.path.basename(path)),  # In parent/gui_app
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", os.path.basename(path)),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(path))
        ]
        
        # Try each path and log results
        print("\nTrying possible paths:")
        for test_path in possible_paths:
            print(f"- Testing path: {test_path}")
            if os.path.exists(test_path):
                print(f"  ✓ FOUND at: {test_path}")
                return test_path
            else:
                print(f"  ✗ Not found")
                
        # If we get here, none of the paths worked - return original and hope for the best
        print(f"\n⚠️ WARNING: Could not find file: {path}. Will try the original path.")
        return path

    def _find_file_recursively(self, start_dir, filename):
        """
        Find a file recursively in a directory structure
        
        Args:
            start_dir: Starting directory
            filename: File name to find (can be partial)
        
        Returns:
            List of found file paths
        """
        found_files = []
        
        try:
            print(f"Searching recursively for '{filename}' in '{start_dir}'")
            for root, dirs, files in os.walk(start_dir):
                for file in files:
                    if filename in file:
                        found_path = os.path.join(root, file)
                        found_files.append(found_path)
                        print(f"Found matching file: {found_path}")
        except Exception as e:
            print(f"Error in recursive search: {e}")
        
        return found_files

    def _load_download_history(self):
        """Load download history and organize by playlist"""
        print("\n=== _load_download_history ===")
        print(f"Looking for history file at: {self.history_file}")
        
        try:
            # Try to find the file if it doesn't exist at the original path
            if not os.path.exists(self.history_file):
                print(f"History file not found at: {self.history_file}")
                
                # Try alternate paths with more options
                alt_paths = [
                    "gui_app/download_history.json",
                    "download_history.json",
                    os.path.join("gui_app", "download_history.json"),
                    os.path.join(parent_dir, "gui_app", "download_history.json"),
                    os.path.join(parent_dir, "download_history.json"),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "gui_app", "download_history.json"),
                    # Try to locate the file anywhere recursively
                    *self._find_file_recursively(parent_dir, "download_history.json")
                ]
                
                print("\nTrying alternate paths for history file:")
                for path in alt_paths:
                    print(f"- Testing: {path}")
                    if os.path.exists(path):
                        self.history_file = path
                        print(f"  ✓ FOUND at: {path}")
                        self.status_var.set(f"Found history file at: {path}")
                        break
                    else:
                        print("  ✗ Not found")
                
                # If still not found, report error
                if not os.path.exists(self.history_file):
                    print("❌ History file not found at any location!")
                    self.status_var.set(f"Download history file not found: {self.history_file}")
                    
                    # Let's check if we can find ANY json files to use as fallback
                    json_files = self._find_file_recursively(parent_dir, ".json")
                    if json_files:
                        print(f"\nFound {len(json_files)} JSON files in project:")
                        for i, file in enumerate(json_files):
                            print(f"{i+1}. {file}")
                    
                    # Try to find playlists from directory structure as a fallback
                    print("\nTrying to find playlists from directory structure...")
                    self._try_find_playlists_from_directories()
                    return
            
            print(f"\nLoading history file from: {self.history_file}")
            
            # Load the history file
            with open(self.history_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                print(f"File size: {len(raw_content)} bytes")
                print(f"Content preview: {raw_content[:200]}...")
                
                history = json.loads(raw_content)
            
            # Debug info
            print(f"\nHistory file contains keys: {list(history.keys())}")
            print(f"Videos key exists: {'videos' in history}")
            
            if 'videos' in history:
                print(f"Number of videos: {len(history['videos'])}")
            
            self.status_var.set(f"Loading {len(history.get('videos', {}))} videos from history...")
            
            # Process videos and organize by playlist
            self.playlists = {}
            valid_tracks = 0
            
            print("\nProcessing videos from history...")
            for video_id, video_info in history.get("videos", {}).items():
                file_path = video_info.get("file_path")
                title = video_info.get("title")
                
                # Skip if no file path or title
                if not file_path or not title:
                    print(f"- Skipping video {video_id}: missing file_path or title")
                    continue
                
                # Print some information about the video
                print(f"\nProcessing video: {title}")
                print(f"- File path: {file_path}")
                
                # Check for playlist info
                print("- Playlist info:", end=" ")
                if "playlist_info" in video_info and video_info["playlist_info"]:
                    print(f"FOUND - {len(video_info['playlist_info'])} playlists")
                    for p in video_info["playlist_info"]:
                        print(f"  - {p.get('name', 'Unnamed')} (ID: {p.get('id', 'Unknown')})")
                else:
                    print("NOT FOUND")
                    
                # Check for old-style playlists array
                print("- Playlists array:", end=" ")
                if "playlists" in video_info and video_info["playlists"]:
                    print(f"FOUND - {len(video_info['playlists'])} playlist IDs")
                    print(f"  - {video_info['playlists']}")
                else:
                    print("NOT FOUND")
                
                # Normalize file path
                if os.path.isabs(file_path):
                    # If it's an absolute path, use it as is
                    normalized_path = file_path
                else:
                    # If it's a relative path, resolve it from the app directory
                    normalized_path = os.path.normpath(os.path.join(parent_dir, file_path))
                
                print(f"- Normalized path: {normalized_path}")
                
                # Check if file exists
                file_exists = os.path.exists(normalized_path)
                print(f"- File exists: {file_exists}")
                
                # Determine playlist name from various sources
                playlist_name = None
                
                # 1. First check playlist_info field with proper playlist name
                if "playlist_info" in video_info and video_info["playlist_info"]:
                    for playlist_info in video_info["playlist_info"]:
                        if playlist_info.get("name") and playlist_info.get("name") != "Unknown Playlist":
                            playlist_name = playlist_info.get("name")
                            break
                
                # 2. Extract from file path if no playlist name found
                if not playlist_name:
                    # Extract from path - look for playlist-like directory names
                    path_parts = Path(normalized_path).parts
                    
                    for part in reversed(path_parts[:-1]):  # Exclude filename
                        if part not in ["data", "audio"]:
                            playlist_name = part
                            break
                
                # 3. Fall back to "Uncategorized" if still no name
                if not playlist_name:
                    playlist_name = "Uncategorized"
                
                print(f"- Assigned to playlist: {playlist_name}")
                
                # Create track info
                track_info = {
                    "id": video_id,
                    "title": title,
                    "file_path": normalized_path,
                    "playlist": playlist_name,
                    "exists": file_exists
                }
                
                # Add to playlist dict
                if playlist_name not in self.playlists:
                    self.playlists[playlist_name] = []
                
                self.playlists[playlist_name].append(track_info)
                valid_tracks += 1
            
            # Check if we found any valid tracks
            print(f"\nFound {valid_tracks} valid tracks in {len(self.playlists)} playlists")
            for playlist_name, tracks in self.playlists.items():
                print(f"- {playlist_name}: {len(tracks)} tracks")

            # Add this section to fix the duplicated paths
            if valid_tracks > 0:
                print("\nChecking for path problems...")
                self._fix_duplicated_paths()
            
            if valid_tracks == 0:
                print("❌ No valid audio tracks found in download history")
                self.status_var.set("No valid audio tracks found in download history")
                # Try to find playlists from directory structure as a fallback
                self._try_find_playlists_from_directories()
            else:
                self.status_var.set(f"Found {valid_tracks} tracks in {len(self.playlists)} playlists")
                
            # Populate the playlist tree
            self._populate_playlist_tree()
                
        except Exception as e:
            import traceback
            print("\n❌ Error loading download history:")
            traceback.print_exc()
            self.status_var.set(f"Error loading download history: {str(e)}")
            messagebox.showerror("Error", f"Failed to load download history: {str(e)}")
            # Try to find playlists from directory structure as a fallback
            self._try_find_playlists_from_directories()
    
    def _try_find_playlists_from_directories(self):
        """Try to find playlists from the audio directory structure as a fallback"""
        print("\n=== _try_find_playlists_from_directories ===")
        try:
            self.status_var.set("Looking for audio files in directories...")
            
            # Find the audio directory - check common locations
            audio_dir_candidates = [
                os.path.join("data", "audio"),
                "audio",
                os.path.join("..", "data", "audio"),
                os.path.join(parent_dir, "data", "audio"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "audio")
            ]
            
            print("Looking for audio directory in:")
            for candidate in audio_dir_candidates:
                print(f"- {candidate}: {'✓ Found' if os.path.isdir(candidate) else '✗ Not found'}")
            
            audio_dir = None
            for candidate in audio_dir_candidates:
                if os.path.isdir(candidate):
                    audio_dir = candidate
                    break
            
            if not audio_dir:
                print("❌ Could not find audio directory")
                
                # Let's try to find any directories with mp3 files
                mp3_dirs = set()
                for root, dirs, files in os.walk(parent_dir):
                    for file in files:
                        if file.endswith('.mp3'):
                            mp3_dirs.add(os.path.dirname(os.path.join(root, file)))
                
                if mp3_dirs:
                    print(f"\nFound {len(mp3_dirs)} directories with MP3 files:")
                    for dir in mp3_dirs:
                        print(f"- {dir}")
                    
                    # Use the directory with the most MP3 files
                    most_mp3s = 0
                    best_dir = None
                    for dir in mp3_dirs:
                        mp3_count = sum(1 for f in os.listdir(dir) if f.endswith('.mp3'))
                        if mp3_count > most_mp3s:
                            most_mp3s = mp3_count
                            best_dir = dir
                    
                    if best_dir:
                        print(f"\nUsing directory with most MP3 files: {best_dir} ({most_mp3s} files)")
                        audio_dir = os.path.dirname(best_dir)  # Use parent dir
                
                if not audio_dir:
                    self.status_var.set("Could not find audio directory")
                    return
                
            print(f"\nUsing audio directory: {audio_dir}")
                
            # Look for subdirectories that could be playlists
            subdirs = [d for d in os.listdir(audio_dir) if os.path.isdir(os.path.join(audio_dir, d))]
            
            print(f"Found {len(subdirs)} subdirectories:")
            for subdir in subdirs:
                print(f"- {subdir}")
            
            if not subdirs:
                print("❌ No playlist directories found")
                self.status_var.set("No playlist directories found")
                return
            
            # Create playlists from subdirectories
            print("\nProcessing subdirectories as playlists:")
            for subdir in subdirs:
                playlist_path = os.path.join(audio_dir, subdir)
                print(f"\nChecking directory: {playlist_path}")
                
                # Find audio files in this directory
                audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
                tracks = []
                
                files_in_dir = os.listdir(playlist_path)
                print(f"- Contains {len(files_in_dir)} files/directories")
                
                for file in files_in_dir:
                    file_path = os.path.join(playlist_path, file)
                    if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in audio_extensions):
                        print(f"  - Found audio file: {file}")
                        # Create track entry
                        track_info = {
                            "id": file,  # Use filename as ID
                            "title": os.path.splitext(file)[0],  # Remove extension
                            "file_path": file_path,
                            "playlist": subdir,
                            "exists": True
                        }
                        tracks.append(track_info)
                
                print(f"- Found {len(tracks)} audio tracks")
                
                # Add to playlists if tracks found
                if tracks:
                    self.playlists[subdir] = tracks
            
            # Check if we found any playlists
            if self.playlists:
                print(f"\n✓ Found {len(self.playlists)} playlists from directories:")
                for name, tracks in self.playlists.items():
                    print(f"- {name}: {len(tracks)} tracks")
                
                self.status_var.set(f"Found {len(self.playlists)} playlists from directories")
                self._populate_playlist_tree()
            else:
                print("❌ No audio files found in directories")
                self.status_var.set("No audio files found in directories")
                
        except Exception as e:
            import traceback
            print("❌ Error finding playlists from directories:")
            traceback.print_exc()
            self.status_var.set(f"Error finding playlists from directories: {str(e)}")

    def _create_widgets(self):
        """Create the audio player interface widgets"""
        # Main layout with left and right panes
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for playlist selection
        left_frame = ttk.Frame(main_pane, padding="5")
        main_pane.add(left_frame, weight=30)
        
        # Right panel for player controls and info
        right_frame = ttk.Frame(main_pane, padding="5")
        main_pane.add(right_frame, weight=70)
        
        # === LEFT PANEL: PLAYLIST SELECTION ===
        ttk.Label(left_frame, text="Available Playlists", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Playlist selection scrollable frame
        playlist_frame = ttk.Frame(left_frame)
        playlist_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for playlist list
        playlist_scroll = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL)
        
        # Playlist treeview
        self.playlist_tree = ttk.Treeview(
            playlist_frame,
            columns=("tracks",),
            show="tree headings",
            yscrollcommand=playlist_scroll.set
        )
        self.playlist_tree.heading("#0", text="Playlist")
        self.playlist_tree.heading("tracks", text="Tracks")
        self.playlist_tree.column("#0", width=200)
        self.playlist_tree.column("tracks", width=50, anchor=tk.CENTER)
        
        playlist_scroll.config(command=self.playlist_tree.yview)
        
        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Playlist selection buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame, 
            text="Select All", 
            command=self._select_all_playlists
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="Deselect All", 
            command=self._deselect_all_playlists
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="Refresh", 
            command=self._refresh_playlists
        ).pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="Check Files",
            command=self._check_files
        ).pack(side=tk.RIGHT, padx=2)
        
        # Current selection info label
        ttk.Label(
            left_frame, 
            textvariable=self.selection_info_var
        ).pack(anchor=tk.W, pady=5)
        
        # === RIGHT PANEL: PLAYER CONTROLS ===
        # Now playing info
        now_playing_frame = ttk.LabelFrame(right_frame, text="Now Playing", padding="10")
        now_playing_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            now_playing_frame,
            textvariable=self.track_title_var,
            font=("Arial", 12),
            wraplength=400
        ).pack(fill=tk.X, pady=5)
        
        ttk.Label(
            now_playing_frame,
            textvariable=self.playlist_name_var,
            font=("Arial", 10, "italic")
        ).pack(fill=tk.X)
        
        # Playback controls
        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Play/Pause button - using text symbols instead of icons for simplicity
        self.play_button = ttk.Button(
            controls_frame,
            text="▶ Play",
            command=self._toggle_playback,
            width=12
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Skip button
        ttk.Button(
            controls_frame,
            text="⏭ Skip",
            command=self._skip_track,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Stop button
        ttk.Button(
            controls_frame,
            text="⏹ Stop",
            command=self._stop_playback,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Volume control
        volume_frame = ttk.Frame(controls_frame)
        volume_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)
        
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self._set_volume,
            length=100
        )
        volume_scale.pack(side=tk.LEFT, padx=5)
        
        volume_label = ttk.Label(volume_frame, width=3, text=f"{self.current_volume}")
        volume_label.pack(side=tk.LEFT)
        
        # Update volume label when slider changes
        def update_volume_label(*args):
            volume_label.config(text=f"{self.volume_var.get()}")
        
        self.volume_var.trace_add("write", update_volume_label)
        
        # Queue section
        queue_frame = ttk.LabelFrame(right_frame, text="Playback Queue", padding="5")
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Queue list with scrollbar
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.BOTH, expand=True)
        
        queue_scroll = ttk.Scrollbar(queue_list_frame, orient=tk.VERTICAL)
        
        self.queue_listbox = tk.Listbox(
            queue_list_frame,
            yscrollcommand=queue_scroll.set,
            selectmode=tk.SINGLE,
            height=10
        )
        
        queue_scroll.config(command=self.queue_listbox.yview)
        
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        queue_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Queue control buttons
        queue_button_frame = ttk.Frame(queue_frame)
        queue_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            queue_button_frame,
            text="Add Random",
            command=self._add_random_to_queue
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            queue_button_frame,
            text="Clear Queue",
            command=self._clear_queue
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            queue_button_frame,
            text="Remove Selected",
            command=self._remove_selected_from_queue
        ).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        # Bind playlist tree selection event
        self.playlist_tree.bind("<ButtonRelease-1>", self._on_playlist_select)
        
        # Double-click on queue to play immediately
        self.queue_listbox.bind("<Double-1>", self._play_selected_from_queue)
        
        # If pygame is not available, show warning
        if not PYGAME_AVAILABLE:
            messagebox.showwarning(
                "Missing Dependency",
                "Pygame is not installed. Audio playback will not work.\n\n"
                "Please install pygame using:\npip install pygame"
            )
            self.status_var.set("ERROR: Pygame not installed. Playback unavailable.")
    
    def _fix_duplicated_paths(self):
        """
        Fix paths that contain duplicated directory structures
        This addresses the issue where paths are stored as 'data/audio/Playlist/data/audio/Playlist/file.mp3'
        """
        print("\n=== Fixing duplicated paths ===")
        
        fixed_count = 0
        for playlist_name, tracks in self.playlists.items():
            for track in tracks:
                file_path = track["file_path"]
                
                # Check for duplicated directory patterns
                if "data/audio" in file_path and file_path.count("data/audio") > 1:
                    # Try to fix the path by removing duplicates
                    parts = file_path.split("data/audio")
                    if len(parts) > 2:
                        # Keep only the first occurrence
                        simplified_path = "data/audio" + parts[-1]
                        print(f"Path correction:\nOld: {file_path}\nNew: {simplified_path}")
                        
                        # Update with corrected path
                        track["file_path"] = simplified_path
                        
                        # Check if the corrected path exists
                        normalized_path = os.path.normpath(os.path.join(parent_dir, simplified_path))
                        exists = os.path.exists(normalized_path)
                        track["exists"] = exists
                        
                        if exists:
                            print(f"✓ Corrected path exists: {normalized_path}")
                            fixed_count += 1
                        else:
                            print(f"✗ Corrected path does not exist: {normalized_path}")
                
                # Also check for backslash version
                elif "data\\audio" in file_path and file_path.count("data\\audio") > 1:
                    # Try to fix the path by removing duplicates
                    parts = file_path.split("data\\audio")
                    if len(parts) > 2:
                        # Keep only the first occurrence
                        simplified_path = "data\\audio" + parts[-1]
                        print(f"Path correction:\nOld: {file_path}\nNew: {simplified_path}")
                        
                        # Update with corrected path
                        track["file_path"] = simplified_path
                        
                        # Check if the corrected path exists
                        normalized_path = os.path.normpath(os.path.join(parent_dir, simplified_path))
                        exists = os.path.exists(normalized_path)
                        track["exists"] = exists
                        
                        if exists:
                            print(f"✓ Corrected path exists: {normalized_path}")
                            fixed_count += 1
                        else:
                            print(f"✗ Corrected path does not exist: {normalized_path}")
        
        # Try even more aggressively to find files
        if fixed_count == 0:
            print("\nTrying more aggressive path correction...")
            for playlist_name, tracks in self.playlists.items():
                for track in tracks:
                    # Extract just the filename
                    filename = os.path.basename(track["file_path"])
                    
                    # Look for this file in common audio directories
                    possible_locations = [
                        os.path.join("data", "audio", playlist_name, filename),
                        os.path.join(parent_dir, "data", "audio", playlist_name, filename)
                    ]
                    
                    for location in possible_locations:
                        if os.path.exists(location):
                            print(f"Found file by name search:\nOld: {track['file_path']}\nNew: {location}")
                            track["file_path"] = location
                            track["exists"] = True
                            fixed_count += 1
                            break
        
        print(f"\nFixed {fixed_count} file paths")
        return fixed_count > 0

    def _populate_playlist_tree(self):
        """Populate the playlist tree with available playlists"""
        print("\n=== _populate_playlist_tree ===")
        
        # Clear existing items
        print("Clearing existing items from tree")
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
        
        if not self.playlists:
            print("❌ No playlists to display")
            self.status_var.set("No playlists found in download history")
            return
        
        # Sort playlists by name
        sorted_playlists = sorted(self.playlists.items())
        print(f"Populating tree with {len(sorted_playlists)} playlists")
        
        # Add playlists to the tree
        for playlist_name, tracks in sorted_playlists:
            print(f"\nAdding playlist: {playlist_name}")
            print(f"- Contains {len(tracks)} tracks")
            
            # Skip empty playlists
            if not tracks:
                print("- Skipping: No tracks")
                continue
                
            # Count tracks that actually exist on disk
            existing_tracks = sum(1 for t in tracks if t.get("exists", False) or os.path.exists(t.get("file_path", "")))
            print(f"- Existing tracks: {existing_tracks}/{len(tracks)}")
            
            # Skip if no tracks exist (but log it)
            if existing_tracks == 0:
                print("- Skipping: No existing tracks")
                continue
                
            # Use a checkmark for selected playlists, empty for unselected
            icon = "✓" if playlist_name in self.selected_playlists else ""
            
            try:
                item_id = self.playlist_tree.insert(
                    "",
                    tk.END,
                    text=f"{icon} {playlist_name}",
                    values=(f"{existing_tracks}/{len(tracks)}",),
                    tags=(playlist_name,)
                )
                print(f"- Added to tree with ID: {item_id}")
            except Exception as e:
                print(f"❌ Error adding playlist {playlist_name} to tree: {str(e)}")
                self.status_var.set(f"Error adding playlist {playlist_name} to tree: {str(e)}")
        
        # If no playlists were added, show a message
        if not self.playlist_tree.get_children():
            print("❌ No valid playlists were added to the tree")
            self.status_var.set("No valid playlists found. Please download videos first.")
        else:
            tree_items = self.playlist_tree.get_children()
            print(f"\n✓ Successfully added {len(tree_items)} playlists to the tree")
            self.status_var.set(f"Loaded {len(tree_items)} playlists")
        
        # Update the selection info
        self._update_selection_info()
    
    def _on_playlist_select(self, event):
        """Handle playlist selection"""
        selection = self.playlist_tree.selection()
        if not selection:
            return
            
        # Get the selected item
        item_id = selection[0]
        
        # Get the playlist name from the tag
        tags = self.playlist_tree.item(item_id, "tags")
        if not tags or not tags[0]:
            return
            
        playlist_name = tags[0]
        
        # Toggle selection status
        if playlist_name in self.selected_playlists:
            self.selected_playlists.remove(playlist_name)
            self.playlist_tree.item(item_id, text=f"  {playlist_name}")
        else:
            self.selected_playlists.add(playlist_name)
            self.playlist_tree.item(item_id, text=f"✓ {playlist_name}")
        
        # Update the selection info
        self._update_selection_info()
    
    def _update_selection_info(self):
        """Update the selection info label"""
        if not self.selected_playlists:
            self.selection_info_var.set("No playlists selected")
            return
            
        total_tracks = 0
        existing_tracks = 0
        
        for playlist_name in self.selected_playlists:
            if playlist_name in self.playlists:
                playlist_tracks = self.playlists[playlist_name]
                total_tracks += len(playlist_tracks)
                existing_tracks += sum(1 for t in playlist_tracks if t["exists"])
        
        self.selection_info_var.set(
            f"{len(self.selected_playlists)} playlists selected with {existing_tracks} available tracks"
        )
    
    def _select_all_playlists(self):
        """Select all playlists"""
        # Get all playlist names from the tree
        for item_id in self.playlist_tree.get_children():
            tags = self.playlist_tree.item(item_id, "tags")
            if tags and tags[0]:
                playlist_name = tags[0]
                self.selected_playlists.add(playlist_name)
                self.playlist_tree.item(item_id, text=f"✓ {playlist_name}")
        
        self._update_selection_info()
    
    def _deselect_all_playlists(self):
        """Deselect all playlists"""
        # Clear selected playlists
        self.selected_playlists.clear()
        
        # Update tree items
        for item_id in self.playlist_tree.get_children():
            tags = self.playlist_tree.item(item_id, "tags")
            if tags and tags[0]:
                playlist_name = tags[0]
                self.playlist_tree.item(item_id, text=f"  {playlist_name}")
        
        self._update_selection_info()
    
    def _refresh_playlists(self):
        """Refresh the playlist list"""
        self.status_var.set("Refreshing playlists...")
        self._load_download_history()
        self.status_var.set("Playlists refreshed")
    
    def _check_files(self):
        """Check if audio files exist and show report"""
        self.status_var.set("Checking audio files...")
        
        total_files = 0
        missing_files = 0
        playlist_stats = {}
        
        # Check all tracks in all playlists
        for playlist_name, tracks in self.playlists.items():
            total_in_playlist = len(tracks)
            missing_in_playlist = 0
            
            for track in tracks:
                total_files += 1
                file_path = track.get("file_path", "")
                
                if not file_path or not os.path.exists(file_path):
                    missing_files += 1
                    missing_in_playlist += 1
                    track["exists"] = False
                else:
                    track["exists"] = True
            
            playlist_stats[playlist_name] = {
                "total": total_in_playlist,
                "missing": missing_in_playlist
            }
        
        # Create detailed report
        report = f"File Check Report:\n\n"
        report += f"Total audio files: {total_files}\n"
        report += f"Missing files: {missing_files}\n\n"
        report += "Playlist Details:\n"
        
        for name, stats in sorted(playlist_stats.items()):
            report += f"- {name}: {stats['total'] - stats['missing']}/{stats['total']} files found"
            if stats["missing"] > 0:
                report += f" ({stats['missing']} missing)"
            report += "\n"
        
        if total_files == 0:
            report += "\nNo audio files found in the download history."
            report += "\nPossible reasons:"
            report += "\n- No videos have been downloaded yet"
            report += "\n- Download history file is empty or corrupt"
            report += "\n- Downloaded files have been moved or deleted"
        elif missing_files > 0:
            report += "\nSome files are missing. This could be because:"
            report += "\n- Files have been moved or deleted"
            report += "\n- The file paths in the download history are incorrect"
            report += "\n- The audio files are on another drive or location"
            report += "\n\nSuggestion: Verify the paths in your download history file"
        
        # Show report
        messagebox.showinfo("File Check Report", report)
        
        # Update playlist display
        self._populate_playlist_tree()
        self.status_var.set(f"File check complete: {missing_files} missing out of {total_files} total")
    
    def _toggle_playback(self):
        """Toggle between play and pause"""
        if not PYGAME_AVAILABLE:
            self.status_var.set("ERROR: Pygame not installed. Playback unavailable.")
            return
            
        if self.is_playing:
            # Pause playback
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.config(text="▶ Play")
            self.status_var.set("Playback paused")
        else:
            # Resume if paused or start new track if nothing playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.play_button.config(text="⏸ Pause")
                self.status_var.set("Playback resumed")
            else:
                # Nothing is playing, try to play next track
                if not self.current_track and not self.playlist_queue:
                    # Add a random track if queue is empty
                    self._add_random_to_queue()
                
                self._play_next_track()
    
    def _play_next_track(self):
        """Play the next track in the queue"""
        if not PYGAME_AVAILABLE:
            self.status_var.set("ERROR: Pygame not installed. Playback unavailable.")
            return
            
        if not self.playlist_queue:
            # Try adding random tracks if queue is empty
            for _ in range(3):  # Try to add 3 tracks
                self._add_random_to_queue()
            
            if not self.playlist_queue:
                self.status_var.set("No tracks available to play. Please select a playlist.")
                return
        
        # Get the next track
        self.current_track = self.playlist_queue.pop(0)
        
        # Update queue display
        self._update_queue_display()
        
        # Update now playing display
        self.track_title_var.set(self.current_track["title"])
        self.playlist_name_var.set(f"From: {self.current_track['playlist']}")
        
        # Start playback
        try:
            if not os.path.exists(self.current_track["file_path"]):
                self.status_var.set(f"Error: File not found: {self.current_track['file_path']}")
                # Try next track
                self.current_track = None
                self._play_next_track()
                return
                
            pygame.mixer.music.load(self.current_track["file_path"])
            pygame.mixer.music.play()
            self.is_playing = True
            self.play_button.config(text="⏸ Pause")
            self.status_var.set(f"Now playing: {self.current_track['title']}")
            
            # Add to history
            self.track_history.append(self.current_track)
            if len(self.track_history) > 50:  # Limit history size
                self.track_history.pop(0)
        except Exception as e:
            self.status_var.set(f"Error playing track: {str(e)}")
            # Try to play the next track
            self.current_track = None
            self._play_next_track()
    
    def _skip_track(self):
        """Skip to the next track"""
        if not PYGAME_AVAILABLE:
            self.status_var.set("ERROR: Pygame not installed. Playback unavailable.")
            return
            
        # Stop current playback
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.config(text="▶ Play")
        
        # Play next track
        self._play_next_track()
    
    def _stop_playback(self):
        """Stop playback completely"""
        if not PYGAME_AVAILABLE:
            self.status_var.set("ERROR: Pygame not installed. Playback unavailable.")
            return
            
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.config(text="▶ Play")
        self.current_track = None
        self.track_title_var.set("No track selected")
        self.playlist_name_var.set("")
        self.status_var.set("Playback stopped")
    
    def _set_volume(self, value):
        """Set the playback volume"""
        if not PYGAME_AVAILABLE:
            return
            
        try:
            self.current_volume = int(float(value))
            pygame.mixer.music.set_volume(self.current_volume / 100.0)
        except Exception:
            pass
    
    def _monitor_playback(self):
        """Monitor playback status and play next track when current finishes"""
        if not PYGAME_AVAILABLE:
            return
            
        while True:
            try:
                if self.is_playing and not pygame.mixer.music.get_busy():
                    # Current track finished, play next track
                    self.current_track = None
                    # Use after to run in main thread
                    self.after(100, self._play_next_track)
                
                # Sleep to prevent CPU usage
                time.sleep(0.5)
            except Exception:
                # Prevent any thread errors from crashing
                time.sleep(1.0)
    
    def _get_random_track(self) -> Optional[Dict]:
        """Get a random track from selected playlists"""
        if not self.selected_playlists:
            self.status_var.set("Please select at least one playlist")
            return None
            
        # Collect all tracks from selected playlists that exist on disk
        valid_tracks = []
        for playlist_name in self.selected_playlists:
            if playlist_name in self.playlists:
                for track in self.playlists[playlist_name]:
                    if track["exists"] or os.path.exists(track["file_path"]):
                        valid_tracks.append(track)
        
        if not valid_tracks:
            self.status_var.set("No valid tracks found in selected playlists")
            return None
            
        # Select a random track
        return random.choice(valid_tracks)
    
    def _add_random_to_queue(self):
        """Add a random track to the playback queue"""
        track = self._get_random_track()
        if track:
            self.playlist_queue.append(track)
            self._update_queue_display()
            self.status_var.set(f"Added to queue: {track['title']}")
        else:
            self.status_var.set("No tracks available. Please select at least one playlist.")
    
    def _clear_queue(self):
        """Clear the playback queue"""
        self.playlist_queue = []
        self._update_queue_display()
        self.status_var.set("Queue cleared")
    
    def _remove_selected_from_queue(self):
        """Remove the selected track from the queue"""
        selection = self.queue_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if 0 <= index < len(self.playlist_queue):
            removed = self.playlist_queue.pop(index)
            self._update_queue_display()
            self.status_var.set(f"Removed from queue: {removed['title']}")
    
    def _play_selected_from_queue(self, event):
        """Play the selected track from the queue immediately"""
        selection = self.queue_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if 0 <= index < len(self.playlist_queue):
            # Get the selected track
            track = self.playlist_queue.pop(index)
            
            # If something is already playing, stop it
            if self.is_playing:
                pygame.mixer.music.stop()
            
            # Insert the track at the beginning of the queue
            self.playlist_queue.insert(0, track)
            
            # Play it
            self.current_track = None
            self._play_next_track()
    
    def _update_queue_display(self):
        """Update the queue listbox display"""
        self.queue_listbox.delete(0, tk.END)
        
        for track in self.playlist_queue:
            self.queue_listbox.insert(tk.END, f"{track['title']} ({track['playlist']})")