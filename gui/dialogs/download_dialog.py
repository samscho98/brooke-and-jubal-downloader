"""
Download dialog for handling video and playlist downloads.
"""
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

from downloader.youtube import YouTubeDownloader
from downloader.tracker import DownloadTracker

class DownloadWorker(QThread):
    """Background worker thread for downloads."""
    
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str, dict)  # success, message, file_info
    
    def __init__(self, downloader, url, playlist_name=None):
        """
        Initialize the download worker.
        
        Args:
            downloader: YouTubeDownloader instance
            url: YouTube URL to download
            playlist_name: Optional playlist name for organization
        """
        super().__init__()
        self.downloader = downloader
        self.url = url
        self.playlist_name = playlist_name or "Other"
        
    def run(self):
        """Run the download operation."""
        try:
            self.progress_signal.emit(10, "Fetching video information...")
            
            # Download the video
            result = self.downloader.download_video(
                self.url, 
                audio_only=True, 
                playlist_name=self.playlist_name
            )
            
            if result:
                downloaded_file, video_info = result
                self.progress_signal.emit(90, "Download completed")
                
                # Prepare return data
                file_info = {
                    "file_path": downloaded_file,
                    "video_id": video_info.get("id", ""),
                    "title": video_info.get("title", "Unknown"),
                    "view_count": video_info.get("view_count", 0),
                    "comment_count": video_info.get("comment_count", 0),
                    "upload_date": video_info.get("upload_date", ""),
                    "duration_seconds": video_info.get("duration", 0)
                }
                
                self.finished_signal.emit(True, "Download completed successfully", file_info)
            else:
                self.progress_signal.emit(90, "Download failed")
                self.finished_signal.emit(False, "Failed to download video", {})
                
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            self.finished_signal.emit(False, f"Error: {str(e)}", {})

class DownloadDialog(QDialog):
    """Dialog for downloading YouTube videos or playlists."""
    
    download_completed = pyqtSignal(bool, dict)  # success, file_info
    
    def __init__(self, parent=None):
        """
        Initialize the download dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Downloading...")
        self.setMinimumWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Get references to required components
        from gui.pages.player_page import PlayerPage
        if isinstance(parent, PlayerPage):
            self.downloader = parent.tracker.downloader
            self.tracker = parent.tracker
        else:
            # If parent is not PlayerPage, try to get from main window
            main_window = parent
            while main_window and not hasattr(main_window, 'downloader'):
                main_window = main_window.parent()
                
            if main_window:
                self.downloader = main_window.downloader
                self.tracker = main_window.tracker
            else:
                raise ValueError("Could not find downloader and tracker instances")
        
        # Initialize UI
        self.init_ui()
        
        # Download worker
        self.download_worker = None
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Preparing download...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def start_download(self, url, playlist_name=None):
        """
        Start downloading a video or playlist.
        
        Args:
            url: YouTube URL to download
            playlist_name: Optional playlist name for organization
        """
        # Create worker thread
        self.download_worker = DownloadWorker(self.downloader, url, playlist_name)
        self.download_worker.progress_signal.connect(self.update_progress)
        self.download_worker.finished_signal.connect(self.download_finished)
        
        # Start the thread
        self.download_worker.start()
        
        # Show the dialog
        self.exec_()
        
    def update_progress(self, value, message):
        """
        Update progress dialog.
        
        Args:
            value: Progress value (0-100)
            message: Status message
        """
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def download_finished(self, success, message, file_info):
        """
        Handle download completion.
        
        Args:
            success: Whether the download was successful
            message: Completion message
            file_info: Information about the downloaded file
        """
        self.progress_bar.setValue(100)
        self.status_label.setText(message)
        
        if success:
            # Add to tracker's download history
            video_id = file_info.get("video_id", "")
            if video_id:
                self.tracker.add_downloaded_video(
                    video_id=video_id,
                    playlist_id="other_videos",  # For single videos
                    title=file_info.get("title", "Unknown"),
                    file_path=file_info.get("file_path", ""),
                    view_count=file_info.get("view_count", 0),
                    comment_count=file_info.get("comment_count", 0),
                    upload_date=file_info.get("upload_date", ""),
                    duration_seconds=file_info.get("duration_seconds", 0)
                )
        
        # Emit completion signal
        self.download_completed.emit(success, file_info)
        
        # Close the dialog
        self.accept()
        
    def cancel_download(self):
        """Cancel the current download operation."""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.terminate()
            self.download_worker = None
            logging.info("Download canceled by user")
            self.reject()