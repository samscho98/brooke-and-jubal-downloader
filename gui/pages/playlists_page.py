"""
Playlist management page for the YouTube Playlist Downloader.
"""
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QLineEdit, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QAbstractItemView, QProgressDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont

from downloader.youtube import YouTubeDownloader
from downloader.tracker import DownloadTracker

class WorkerThread(QThread):
    """Background worker thread for downloads."""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str, int, int)
    
    def __init__(self, downloader, url, operation_type, playlist_name=None):
        super().__init__()
        self.downloader = downloader
        self.url = url
        self.operation_type = operation_type  # "playlist" or "video"
        self.playlist_name = playlist_name
        
    def run(self):
        try:
            if self.operation_type == "playlist":
                # Get playlist videos
                self.progress_signal.emit(10, "Loading playlist info...")
                videos = self.downloader.get_playlist_videos(self.url)
                
                if not videos:
                    self.finished_signal.emit(False, "No videos found in playlist", 0, 0)
                    return
                    
                self.progress_signal.emit(30, f"Found {len(videos)} videos in playlist")
                
                # Download videos
                successful = []
                failed = []
                
                for i, video in enumerate(videos):
                    progress = 30 + int(60 * (i / len(videos)))
                    self.progress_signal.emit(progress, f"Downloading {i+1}/{len(videos)}: {video['title']}")
                    
                    video_url = video['url']
                    result = self.downloader.download_video(video_url, audio_only=True, playlist_name=self.playlist_name)
                    
                    if result:
                        successful.append(result)
                    else:
                        failed.append(video['id'])
                        
                self.progress_signal.emit(95, "Completing download...")
                self.finished_signal.emit(True, "Playlist download completed", len(successful), len(failed))
                
            elif self.operation_type == "video":
                # Download single video
                self.progress_signal.emit(20, "Loading video info...")
                result = self.downloader.download_video(self.url, audio_only=True)
                
                if result:
                    self.progress_signal.emit(90, "Download completed")
                    self.finished_signal.emit(True, "Video downloaded successfully", 1, 0)
                else:
                    self.progress_signal.emit(90, "Download failed")
                    self.finished_signal.emit(False, "Failed to download video", 0, 1)
        
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            self.finished_signal.emit(False, f"Error: {str(e)}", 0, 0)


class PlaylistsPage(QWidget):
    """Playlist management page."""
    
    # Signal emitted when a playlist is updated
    playlist_updated = pyqtSignal()
    
    def __init__(self, downloader: YouTubeDownloader, tracker: DownloadTracker):
        """
        Initialize the playlists page.
        
        Args:
            downloader: YouTube downloader instance
            tracker: Download tracker instance
        """
        super().__init__()
        self.downloader = downloader
        self.tracker = tracker
        
        # Current download operation
        self.download_thread = None
        self.progress_dialog = None
        
        # Set up UI
        self.setup_ui()
        
        # Load playlists
        self.load_playlists()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Add playlist section
        add_section = QGroupBox("Add Playlist")
        add_layout = QVBoxLayout(add_section)
        
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube playlist URL here")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name for this playlist")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        check_interval_layout = QHBoxLayout()
        check_interval_label = QLabel("Check Interval (hours):")
        self.check_interval_input = QSpinBox()
        self.check_interval_input.setRange(1, 168)  # 1 hour to 7 days
        self.check_interval_input.setValue(24)      # Default 24 hours
        check_interval_layout.addWidget(check_interval_label)
        check_interval_layout.addWidget(self.check_interval_input)
        
        add_button_layout = QHBoxLayout()
        add_button_layout.addStretch()
        self.add_playlist_button = QPushButton("Add Playlist")
        self.add_playlist_button.clicked.connect(self.add_playlist)
        add_button_layout.addWidget(self.add_playlist_button)
        
        add_layout.addLayout(url_layout)
        add_layout.addLayout(name_layout)
        add_layout.addLayout(check_interval_layout)
        add_layout.addLayout(add_button_layout)
        
        # Playlists section
        playlists_section = QGroupBox("Tracked Playlists")
        playlists_layout = QVBoxLayout(playlists_section)
        
        self.playlists_table = QTableWidget(0, 5)
        self.playlists_table.setHorizontalHeaderLabels(["Name", "URL", "Videos", "Last Update", "Actions"])
        self.playlists_table.verticalHeader().setVisible(False)
        self.playlists_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.playlists_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.Interactive)  # Name
        header.resizeSection(0, 200)
        header.setSectionResizeMode(1, header.Stretch)      # URL
        header.setSectionResizeMode(2, header.ResizeToContents)  # Videos
        header.setSectionResizeMode(3, header.Interactive)  # Last Update
        header.resizeSection(3, 150)
        header.setSectionResizeMode(4, header.Interactive)  # Actions
        header.resizeSection(4, 200)
        
        self.playlists_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #121A21;
                color: white;
                padding: 4px;
                border: none;
            }
        """)
        
        playlists_buttons_layout = QHBoxLayout()
        playlists_buttons_layout.addStretch()
        
        update_all_button = QPushButton("Update All Playlists")
        update_all_button.clicked.connect(self.update_all_playlists)
        
        refresh_list_button = QPushButton("Refresh List")
        refresh_list_button.clicked.connect(self.load_playlists)
        
        playlists_buttons_layout.addWidget(refresh_list_button)
        playlists_buttons_layout.addWidget(update_all_button)
        
        playlists_layout.addWidget(self.playlists_table)
        playlists_layout.addLayout(playlists_buttons_layout)
        
        # Direct download section
        direct_section = QGroupBox("Direct Download")
        direct_layout = QVBoxLayout(direct_section)
        
        direct_url_layout = QHBoxLayout()
        direct_url_label = QLabel("URL:")
        self.direct_url_input = QLineEdit()
        self.direct_url_input.setPlaceholderText("Paste YouTube video URL here")
        direct_url_layout.addWidget(direct_url_label)
        direct_url_layout.addWidget(self.direct_url_input)
        
        direct_button_layout = QHBoxLayout()
        direct_button_layout.addStretch()
        
        self.direct_download_button = QPushButton("Download")
        self.direct_download_button.clicked.connect(self.direct_download)
        direct_button_layout.addWidget(self.direct_download_button)
        
        direct_layout.addLayout(direct_url_layout)
        direct_layout.addLayout(direct_button_layout)
        
        # Assemble layout
        layout.addWidget(add_section)
        layout.addWidget(playlists_section)
        layout.addWidget(direct_section)
        
    def load_playlists(self):
        """Load playlists into the table."""
        try:
            # Clear the table
            self.playlists_table.setRowCount(0)
            
            # Get playlists
            playlists = self.tracker.get_playlists()
            
            for playlist in playlists:
                row = self.playlists_table.rowCount()
                self.playlists_table.insertRow(row)
                
                # Set name
                name = playlist.get('name', 'Unknown')
                self.playlists_table.setItem(row, 0, QTableWidgetItem(name))
                
                # Set URL
                url = playlist.get('url', '')
                url_item = QTableWidgetItem(url)
                # Store full URL as data
                url_item.setData(Qt.UserRole, url)
                self.playlists_table.setItem(row, 1, url_item)
                
                # Set video count (placeholder)
                video_count = "0"  # We'll need to calculate this
                self.playlists_table.setItem(row, 2, QTableWidgetItem(video_count))
                
                # Set last updated
                last_checked = playlist.get('last_checked', 'Never')
                if last_checked and last_checked != 'Never':
                    try:
                        dt = datetime.fromisoformat(last_checked)
                        last_checked = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                        
                self.playlists_table.setItem(row, 3, QTableWidgetItem(last_checked))
                
                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                update_button = QPushButton("Update")
                update_button.setProperty("url", url)
                update_button.clicked.connect(self.update_playlist)
                
                remove_button = QPushButton("Remove")
                remove_button.setProperty("url", url)
                remove_button.clicked.connect(self.remove_playlist)
                
                actions_layout.addWidget(update_button)
                actions_layout.addWidget(remove_button)
                
                self.playlists_table.setCellWidget(row, 4, actions_widget)
            
            logging.info(f"Loaded {len(playlists)} playlists")
            
        except Exception as e:
            logging.error(f"Error loading playlists: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load playlists: {str(e)}")
    
    def add_playlist(self):
        """Add a new playlist to track."""
        url = self.url_input.text().strip()
        name = self.name_input.text().strip()
        check_interval = self.check_interval_input.value()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a playlist URL")
            return
            
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a playlist name")
            return
            
        try:
            # Validate URL is a YouTube playlist
            if "youtube.com/playlist" not in url and "list=" not in url:
                QMessageBox.warning(self, "Error", "This doesn't appear to be a valid YouTube playlist URL")
                return
            
            # Add the playlist
            success = self.tracker.add_playlist(
                url=url,
                name=name,
                check_interval=check_interval
            )
            
            if success:
                QMessageBox.information(self, "Success", f"Successfully added playlist: {name}")
                
                # Clear inputs
                self.url_input.clear()
                self.name_input.clear()
                
                # Reload playlists
                self.load_playlists()
                
                # Ask if they want to download now
                download_now = QMessageBox.question(
                    self, 
                    "Download Now?", 
                    "Would you like to download this playlist now?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if download_now == QMessageBox.Yes:
                    self.start_download(url, name)
            else:
                QMessageBox.warning(self, "Error", "Failed to add playlist")
                
        except Exception as e:
            logging.error(f"Error adding playlist: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to add playlist: {str(e)}")
    
    def update_playlist(self):
        """Update a specific playlist."""
        button = self.sender()
        if not button:
            return
            
        url = button.property("url")
        if not url:
            return
            
        # Find the playlist name
        playlist_name = None
        for playlist in self.tracker.get_playlists():
            if playlist["url"] == url:
                playlist_name = playlist.get("name", "Unknown")
                break
                
        # Confirm the update
        confirm = QMessageBox.question(
            self, 
            "Update Playlist", 
            f"Do you want to update the playlist: {playlist_name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.start_download(url, playlist_name)
            
    def start_download(self, url, playlist_name):
        """Start a download operation."""
        # Create progress dialog
        self.progress_dialog = QProgressDialog("Preparing download...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Downloading Playlist")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.canceled.connect(self.cancel_download)
        
        # Create worker thread
        self.download_thread = WorkerThread(self.downloader, url, "playlist", playlist_name)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        
        # Start the thread
        self.download_thread.start()
        self.progress_dialog.show()
    
    def cancel_download(self):
        """Cancel the current download operation."""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread = None
            logging.info("Download canceled by user")
    
    def update_progress(self, value, message):
        """Update progress dialog."""
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(message)
    
    def download_finished(self, success, message, successful_count, failed_count):
        """Handle download completion."""
        if self.progress_dialog:
            self.progress_dialog.setValue(100)
            self.progress_dialog.close()
            
        if success:
            QMessageBox.information(
                self, 
                "Download Complete", 
                f"{message}\n\nSuccessfully downloaded: {successful_count} videos\nFailed: {failed_count} videos"
            )
            
            # Refresh playlists and emit update signal
            self.load_playlists()
            self.playlist_updated.emit()
        else:
            QMessageBox.warning(self, "Download Error", message)
    
    def remove_playlist(self):
        """Remove a playlist from tracking."""
        button = self.sender()
        if not button:
            return
            
        url = button.property("url")
        if not url:
            return
            
        # Find the playlist name
        playlist_name = None
        for playlist in self.tracker.get_playlists():
            if playlist["url"] == url:
                playlist_name = playlist.get("name", "Unknown")
                break
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Remove Playlist", 
            f"Are you sure you want to remove the playlist: {playlist_name}?\n\nThis will not delete any downloaded files.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.tracker.remove_playlist(url)
            
            if success:
                QMessageBox.information(self, "Success", f"Successfully removed playlist: {playlist_name}")
                self.load_playlists()
            else:
                QMessageBox.warning(self, "Error", "Failed to remove playlist")
    
    def update_all_playlists(self):
        """Update all tracked playlists."""
        playlists = self.tracker.get_playlists()
        
        if not playlists:
            QMessageBox.information(self, "No Playlists", "No playlists are currently being tracked")
            return
            
        # Confirm update
        confirm = QMessageBox.question(
            self, 
            "Update All Playlists", 
            f"Do you want to update all {len(playlists)} playlists?\n\nThis may take a while.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # TODO: Implement batch update
            QMessageBox.information(
                self, 
                "Not Implemented", 
                "Batch update is not yet implemented. Please update playlists individually."
            )
    
    def direct_download(self):
        """Download a single YouTube video."""
        url = self.direct_url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a video URL")
            return
            
        try:
            # Validate URL is a YouTube video
            if "youtube.com/watch" not in url and "youtu.be/" not in url:
                QMessageBox.warning(self, "Error", "This doesn't appear to be a valid YouTube video URL")
                return
            
            # Create progress dialog
            self.progress_dialog = QProgressDialog("Preparing download...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowTitle("Downloading Video")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.canceled.connect(self.cancel_download)
            
            # Create worker thread
            self.download_thread = WorkerThread(self.downloader, url, "video")
            self.download_thread.progress_signal.connect(self.update_progress)
            self.download_thread.finished_signal.connect(self.direct_download_finished)
            
            # Start the thread
            self.download_thread.start()
            self.progress_dialog.show()
                
        except Exception as e:
            logging.error(f"Error in direct download: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to start download: {str(e)}")
    
    def direct_download_finished(self, success, message, successful_count, failed_count):
        """Handle direct download completion."""
        if self.progress_dialog:
            self.progress_dialog.setValue(100)
            self.progress_dialog.close()
            
        if success:
            QMessageBox.information(self, "Download Complete", message)
            self.direct_url_input.clear()
            
            # Emit update signal
            self.playlist_updated.emit()
        else:
            QMessageBox.warning(self, "Download Error", message)