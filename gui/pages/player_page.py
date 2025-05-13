"""
Audio player page for the YouTube Playlist Downloader.
"""
import os
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QAction,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from downloader.tracker import DownloadTracker
from downloader.scoring import ScoringSystem
from audio.player import AudioPlayer

from gui.components.queue_table import QueueTable
from gui.components.audio_controls import AudioControls
from gui.components.time_slider import TimeSlider
from gui.components.volume_control import VolumeControl

class PlayerPage(QWidget):
    """Audio player page."""
    track_played = pyqtSignal(str)  # Emitted when a track is played (video_id)
    
    def __init__(self, tracker, scoring, audio_player, downloader=None):
        super().__init__()
        self.tracker = tracker
        self.scoring = scoring
        self.audio_player = audio_player
        self.current_track = None
        
        # Store reference to the downloader (needed for download dialog)
        self.downloader = downloader
        
        self.init_ui()
        self.connect_signals()
        
        # Initial refresh
        self.refresh_queue()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Input section for URL download
        input_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube video or playlist URL here")
        self.url_input.setMinimumHeight(40)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name (optional)")
        self.name_input.setMinimumHeight(40)
        self.name_input.setFixedWidth(200)
        
        self.download_button = QPushButton("Download")
        self.download_button.setMinimumHeight(40)
        self.download_button.setMinimumWidth(120)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3a92ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.download_button)
        
        # Center section with playlist list and queue table
        center_layout = QHBoxLayout()
        
        # Playlist list
        playlists_layout = QVBoxLayout()
        playlists_label = QLabel("Playlists")
        playlists_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        
        self.playlists_widget = QTableWidget(0, 2)  # Name, Checked
        self.playlists_widget.setHorizontalHeaderLabels(["Name", ""])
        self.playlists_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.playlists_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.playlists_widget.verticalHeader().setVisible(False)
        self.playlists_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.playlists_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.playlists_widget.setMinimumWidth(200)
        self.playlists_widget.setMaximumWidth(250)
        
        self.update_playlists_button = QPushButton("Update Selected")
        self.update_playlists_button.setMinimumHeight(40)
        
        playlists_layout.addWidget(playlists_label)
        playlists_layout.addWidget(self.playlists_widget)
        playlists_layout.addWidget(self.update_playlists_button)
        
        # Queue table
        queue_layout = QVBoxLayout()
        queue_label = QLabel("Current Queue")
        queue_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        
        self.queue_table = QueueTable()
        
        queue_layout.addWidget(queue_label)
        queue_layout.addWidget(self.queue_table)
        
        center_layout.addLayout(playlists_layout)
        center_layout.addLayout(queue_layout)
        
        # Bottom audio controls
        bottom_layout = QVBoxLayout()
        
        # Track info
        self.track_info = QLabel("No track playing")
        self.track_info.setAlignment(Qt.AlignCenter)
        self.track_info.setStyleSheet("font-weight: bold; color: #ffffff;")
        self.track_info.setMinimumHeight(30)
        
        # Time slider
        self.time_slider = TimeSlider()
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Audio controls
        self.audio_controls = AudioControls()
        
        # Volume control
        self.volume_control = VolumeControl()
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.audio_controls)
        controls_layout.addStretch()
        controls_layout.addWidget(self.volume_control)
        
        bottom_layout.addWidget(self.track_info)
        bottom_layout.addWidget(self.time_slider)
        bottom_layout.addLayout(controls_layout)
        
        # Add all sections to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(bottom_layout)
        
        # Set stretch factors
        main_layout.setStretchFactor(center_layout, 1)
    
    def connect_signals(self):
        """Connect all signals."""
        # Download button
        self.download_button.clicked.connect(self.download_clicked)
        
        # Playlists widget
        self.playlists_widget.itemDoubleClicked.connect(self.playlist_double_clicked)
        self.update_playlists_button.clicked.connect(self.update_selected_playlists)
        
        # Queue table
        self.queue_table.play_requested.connect(self.play_track)
        self.queue_table.remove_requested.connect(self.remove_from_queue)
        self.queue_table.itemDoubleClicked.connect(lambda item: self.play_track(item.row()))
        
        # Audio controls
        self.audio_controls.play_clicked.connect(self.audio_player.play)
        self.audio_controls.pause_clicked.connect(self.audio_player.pause)
        self.audio_controls.next_clicked.connect(self.play_next)
        self.audio_controls.previous_clicked.connect(self.play_previous)
        
        # Time slider
        self.time_slider.position_changed.connect(self.audio_player.set_position)
        self.time_slider.slider_pressed.connect(self.audio_player.pause)
        self.time_slider.slider_released.connect(self.audio_player.set_position_and_play)
        
        # Volume control
        self.volume_control.volume_changed.connect(self.audio_player.set_volume)
        
        # Audio player signals
        self.audio_player.track_started.connect(self.on_track_started)
        self.audio_player.position_changed.connect(self.time_slider.update_position)
        self.audio_player.duration_changed.connect(self.time_slider.set_duration)
        self.audio_player.track_ended.connect(self.play_next)
    
    def refresh_playlists(self):
        """Refresh the playlists list."""
        self.playlists_widget.setRowCount(0)
        
        # Get all playlists from tracker
        playlists = self.tracker.get_playlists()
        
        # Add "Other" playlist for single videos
        playlists.append({"name": "Other", "url": "other_videos"})
        
        # Add to table
        for playlist in playlists:
            row = self.playlists_widget.rowCount()
            self.playlists_widget.insertRow(row)
            
            # Name column
            name_item = QTableWidgetItem(playlist["name"])
            self.playlists_widget.setItem(row, 0, name_item)
            
            # Checkbox column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.Unchecked)
            self.playlists_widget.setItem(row, 1, checkbox_item)
    
    def refresh_queue(self):
        """Refresh the queue table with downloaded videos."""
        self.refresh_playlists()
        
        # Get current time slot for scoring
        current_slot = self.scoring.get_current_time_slot()
        
        # Get top videos from scoring system
        top_videos = self.scoring.get_top_videos(time_slot=current_slot, limit=50)
        
        # Clear the table
        self.queue_table.clearContents()
        self.queue_table.setRowCount(0)
        
        # Get downloaded videos from tracker to match with scored videos
        downloaded_videos = {video["id"]: video for video in self.tracker.get_downloaded_videos()}
        
        # Add to table
        for index, video in enumerate(top_videos):
            video_id = video["id"]
            
            # Skip if not in downloaded videos
            if video_id not in downloaded_videos:
                continue
            
            downloaded_video = downloaded_videos[video_id]
            
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)
            
            # Number column
            number_item = QTableWidgetItem(str(index + 1))
            number_item.setTextAlignment(Qt.AlignCenter)
            self.queue_table.setItem(row, 0, number_item)
            
            # Title column
            title_item = QTableWidgetItem(video["title"])
            title_item.setData(Qt.UserRole, video_id)  # Store video_id in user role
            self.queue_table.setItem(row, 1, title_item)
            
            # Playlist column
            playlist_info = ""
            if "playlist_info" in downloaded_video:
                playlist_names = [p["name"] for p in downloaded_video["playlist_info"]]
                playlist_info = ", ".join(playlist_names)
            self.queue_table.setItem(row, 2, QTableWidgetItem(playlist_info))
            
            # Duration column
            duration = ""
            if "duration_minutes" in downloaded_video:
                minutes = int(downloaded_video["duration_minutes"])
                seconds = int((downloaded_video["duration_minutes"] - minutes) * 60)
                duration = f"{minutes}:{seconds:02d}"
            self.queue_table.setItem(row, 3, QTableWidgetItem(duration))
            
            # Score column
            score_item = QTableWidgetItem(f"{video['score']:.1f}")
            score_item.setTextAlignment(Qt.AlignCenter)
            self.queue_table.setItem(row, 4, QTableWidgetItem(score_item))
    
    def download_clicked(self):
        """Handle download button click."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL.")
            return
        
        name = self.name_input.text().strip()
        
        # Determine if it's a playlist or single video
        is_playlist = "list=" in url
        
        if is_playlist:
            # If no name is provided for playlist, request one
            if not name:
                name = "New Playlist"  # Default name
                
            # Create download dialog and start download
            from gui.dialogs.download_dialog import DownloadDialog
            download_dialog = DownloadDialog(self)
            
            # Connect signals
            download_dialog.download_completed.connect(self.on_download_completed)
            
            # Pass downloader and tracker 
            download_dialog.downloader = self.downloader  # Make sure we pass the downloader
            download_dialog.tracker = self.tracker        # Make sure we pass the tracker
            
            # Start the download
            download_dialog.start_download(url, name)
            download_dialog.exec_()  # Show as modal dialog
            
        else:
            # Single video goes to "Other" playlist
            from gui.dialogs.download_dialog import DownloadDialog
            download_dialog = DownloadDialog(self)
            
            # Connect signals
            download_dialog.download_completed.connect(self.on_download_completed)
            
            # Pass downloader and tracker
            download_dialog.downloader = self.downloader  # Make sure we pass the downloader
            download_dialog.tracker = self.tracker        # Make sure we pass the tracker
            
            # Start the download
            download_dialog.start_download(url, "Other")
            download_dialog.exec_()  # Show as modal dialog
        
        # Clear inputs
        self.url_input.clear()
        self.name_input.clear()
    
    def on_download_completed(self, success, message):
        """Handle download completion."""
        if success:
            # Refresh the queue after successful download
            self.refresh_queue()
    
    def playlist_double_clicked(self, item):
        """Handle double click on playlist item."""
        row = item.row()
        playlist_name = self.playlists_widget.item(row, 0).text()
        
        # Show playlist details dialog
        QMessageBox.information(self, "Playlist Details", 
                               f"Details for playlist: {playlist_name}\n\nThis will be implemented in the next phase.")
    
    def update_selected_playlists(self):
        """Update selected playlists."""
        selected_playlists = []
        selected_urls = []
        
        # Get all checked playlists
        for row in range(self.playlists_widget.rowCount()):
            checkbox_item = self.playlists_widget.item(row, 1)
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                playlist_name = self.playlists_widget.item(row, 0).text()
                selected_playlists.append(playlist_name)
                
                # Get URL for this playlist from tracker
                for playlist in self.tracker.get_playlists():
                    if playlist["name"] == playlist_name:
                        selected_urls.append(playlist["url"])
                        break
        
        if not selected_playlists:
            QMessageBox.warning(self, "Selection Error", "Please select at least one playlist to update.")
            return
        
        # Create progress dialog for batch update
        from gui.dialogs.download_dialog import DownloadDialog
        
        # Update each playlist sequentially
        for i, (name, url) in enumerate(zip(selected_playlists, selected_urls)):
            # Skip "Other" placeholder playlist
            if url == "other_videos":
                continue
                
            # Create dialog for this playlist
            download_dialog = DownloadDialog(self)
            download_dialog.setWindowTitle(f"Updating Playlist {i+1}/{len(selected_playlists)}: {name}")
            
            # Configure dialog
            download_dialog.downloader = self.downloader
            download_dialog.tracker = self.tracker
            
            # Connect signals
            download_dialog.download_completed.connect(self.on_download_completed)
            
            # Start the download
            download_dialog.start_download(url, name)
            download_dialog.exec_()
    
    def play_track(self, row):
        """Play the track at the specified row."""
        title_item = self.queue_table.item(row, 1)
        if not title_item:
            return
        
        video_id = title_item.data(Qt.UserRole)
        title = title_item.text()
        
        # Get file path from tracker
        downloaded_videos = self.tracker.get_downloaded_videos()
        file_path = None
        
        for video in downloaded_videos:
            if video["id"] == video_id:
                file_path = video["file_path"]
                break
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Playback Error", f"Could not find audio file for: {title}")
            return
        
        # Update current track and highlight in table
        self.current_track = {"id": video_id, "title": title, "row": row}
        self.queue_table.selectRow(row)
        
        # Start playback
        self.audio_player.load(file_path, video_id)
        self.audio_player.play()
        
        # Update UI
        self.track_info.setText(title)
        
        # Emit signal
        self.track_played.emit(video_id)
    
    def play_next(self):
        """Play the next track in the queue."""
        if self.current_track is None:
            # If no track is playing, play the first one
            if self.queue_table.rowCount() > 0:
                self.play_track(0)
            return
        
        next_row = self.current_track["row"] + 1
        if next_row < self.queue_table.rowCount():
            self.play_track(next_row)
    
    def play_previous(self):
        """Play the previous track in the queue."""
        if self.current_track is None:
            # If no track is playing, play the first one
            if self.queue_table.rowCount() > 0:
                self.play_track(0)
            return
        
        prev_row = self.current_track["row"] - 1
        if prev_row >= 0:
            self.play_track(prev_row)
    
    def remove_from_queue(self, row):
        """Remove a track from the queue."""
        # This doesn't actually remove from file system, just from the queue view
        self.queue_table.removeRow(row)
        
        # Update current track if needed
        if self.current_track is not None:
            if row == self.current_track["row"]:
                # Current track was removed
                self.audio_player.stop()
                self.current_track = None
                self.track_info.setText("No track playing")
            elif row < self.current_track["row"]:
                # A track before current was removed, update index
                self.current_track["row"] -= 1
    
    def on_track_started(self, track_id):
        """Handle when a track starts playing."""
        # Update interface if needed
        if self.current_track and self.current_track["id"] == track_id:
            self.track_info.setText(self.current_track["title"])
            self.audio_controls.set_playing(True)