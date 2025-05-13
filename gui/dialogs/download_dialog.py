"""
Download dialog for YouTube videos and playlists.
"""
import os
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class DownloadWorker(QThread):
    """Worker thread for downloading videos."""
    
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str, int, int)
    
    def __init__(self, downloader, url, operation_type, playlist_name=None):
        super().__init__()
        self.downloader = downloader
        self.url = url
        self.operation_type = operation_type  # "playlist" or "video"
        self.playlist_name = playlist_name
        self.is_cancelled = False
        
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
                
                # Extract playlist ID from URL
                import re
                playlist_id_match = re.search(r'list=([^&]+)', self.url)
                playlist_id = playlist_id_match.group(1) if playlist_id_match else "unknown"
                
                # Download videos
                successful = []
                failed = []
                
                for i, video in enumerate(videos):
                    if self.is_cancelled:
                        self.finished_signal.emit(False, "Download cancelled", len(successful), len(failed))
                        return
                        
                    progress = 30 + int(60 * (i / len(videos)))
                    self.progress_signal.emit(progress, f"Downloading {i+1}/{len(videos)}: {video['title']}")
                    
                    video_url = video['url']
                    result = self.downloader.download_video(video_url, audio_only=True, playlist_name=self.playlist_name)
                    
                    if result:
                        file_path, video_info = result
                        
                        # Add to download history with proper metadata
                        from downloader.tracker import DownloadTracker
                        if hasattr(self, 'tracker') and self.tracker:
                            # Use the provided tracker
                            tracker = self.tracker
                        else:
                            # Create a new tracker as fallback
                            tracker = DownloadTracker()
                            
                        # Add video to tracker
                        video_id = video_info.get('id', '')
                        tracker.add_downloaded_video(
                            video_id=video_id,
                            playlist_id=playlist_id,
                            title=video_info.get('title', 'Unknown Title'),
                            file_path=file_path,
                            view_count=video_info.get('view_count', 0),
                            comment_count=video_info.get('comment_count', 0),
                            upload_date=video_info.get('upload_date'),
                            duration_seconds=video_info.get('duration', 0)
                        )
                        
                        successful.append((file_path, video_info))
                    else:
                        failed.append(video['id'])
                        
                self.progress_signal.emit(95, "Completing download...")
                self.finished_signal.emit(True, "Playlist download completed", len(successful), len(failed))
                
            elif self.operation_type == "video":
                # Download single video
                self.progress_signal.emit(20, "Loading video info...")
                result = self.downloader.download_video(self.url, audio_only=True, playlist_name=self.playlist_name)
                
                if result:
                    file_path, video_info = result
                    video_id = video_info.get('id', '')
                    video_title = video_info.get('title', 'Unknown')
                    
                    # Add to download history
                    from downloader.tracker import DownloadTracker
                    if hasattr(self, 'tracker') and self.tracker:
                        # Use the provided tracker
                        tracker = self.tracker
                    else:
                        # Create a new tracker as fallback
                        tracker = DownloadTracker()
                        
                    # Extract video ID from URL if not in video_info
                    if not video_id:
                        import re
                        video_id_match = re.search(r'v=([^&]+)', self.url)
                        if video_id_match:
                            video_id = video_id_match.group(1)
                        else:
                            video_id = "unknown"
                    
                    # Special 'other' playlist ID for single videos
                    playlist_id = "other_videos"
                    
                    # Add to tracker
                    tracker.add_downloaded_video(
                        video_id=video_id,
                        playlist_id=playlist_id,
                        title=video_title,
                        file_path=file_path,
                        view_count=video_info.get('view_count', 0),
                        comment_count=video_info.get('comment_count', 0),
                        upload_date=video_info.get('upload_date'),
                        duration_seconds=video_info.get('duration', 0)
                    )
                    
                    self.progress_signal.emit(90, f"Downloaded: {video_title}")
                    self.finished_signal.emit(True, f"Video downloaded successfully: {video_title}", 1, 0)
                else:
                    self.progress_signal.emit(90, "Download failed")
                    self.finished_signal.emit(False, "Failed to download video", 0, 1)
        
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            self.finished_signal.emit(False, f"Error: {str(e)}", 0, 0)
    
    def cancel(self):
        """Cancel the download operation."""
        self.is_cancelled = True

class DownloadDialog(QDialog):
    """Dialog for downloading YouTube videos or playlists."""
    
    download_completed = pyqtSignal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get the downloader instance from the parent application
        self.downloader = None
        self.tracker = None
        
        # If parent is Player Page, it should have the downloader available
        if parent and hasattr(parent, 'downloader'):
            self.downloader = parent.downloader
        # If not directly available, try to get from main window
        elif parent and hasattr(parent, 'window') and hasattr(parent.window, 'downloader'):
            self.downloader = parent.window.downloader
        # If still not found, check if our parent has a reference to it
        elif parent and hasattr(parent, 'parent') and hasattr(parent.parent(), 'downloader'):
            self.downloader = parent.parent().downloader
            
        # Similarly for tracker
        if parent and hasattr(parent, 'tracker'):
            self.tracker = parent.tracker
        elif parent and hasattr(parent, 'window') and hasattr(parent.window, 'tracker'):
            self.tracker = parent.window.tracker
        elif parent and hasattr(parent, 'parent') and hasattr(parent.parent(), 'tracker'):
            self.tracker = parent.parent().tracker
            
        if not self.downloader:
            # Create a new downloader as fallback
            from downloader.youtube import YouTubeDownloader
            from data.config_manager import ConfigHandler
            config = ConfigHandler()
            output_dir = config.get("general", "output_directory", "data/audio")
            self.downloader = YouTubeDownloader(output_dir, config)
            logging.warning("DownloadDialog created with a new downloader instance")
            
        if not self.tracker:
            # Create a new tracker as fallback
            from downloader.tracker import DownloadTracker
            self.tracker = DownloadTracker()
            logging.warning("DownloadDialog created with a new tracker instance")
            
        self.worker_thread = None
        self.setup_ui()
        self.setWindowTitle("Download Progress")
        self.resize(500, 200)
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Preparing download...")
        self.status_label.setWordWrap(True)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.close_button)
        
        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)
        
    def start_download(self, url, playlist_name=None):
        """
        Start the download process.
        
        Args:
            url: URL to download (video or playlist)
            playlist_name: Optional name for organizing the download
        """
        if not url:
            QMessageBox.warning(self, "Error", "No URL provided")
            self.close()
            return
            
        # Determine if it's a video or playlist
        is_playlist = "list=" in url
        operation_type = "playlist" if is_playlist else "video"
        
        # Create and start worker thread
        self.worker_thread = DownloadWorker(
            self.downloader, 
            url, 
            operation_type, 
            playlist_name
        )
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.finished_signal.connect(self.download_finished)
        
        self.worker_thread.start()
        
    def update_progress(self, value, message):
        """Update progress bar and status message."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def download_finished(self, success, message, successful_count, failed_count):
        """Handle download completion."""
        self.progress_bar.setValue(100)
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        
        if success:
            self.status_label.setText(f"{message}\n\nSuccessfully downloaded: {successful_count}\nFailed: {failed_count}")
        else:
            self.status_label.setText(f"{message}\n\nSuccessfully downloaded: {successful_count}\nFailed: {failed_count}")
            
        # Make sure the tracker's files are saved
        if self.tracker:
            try:
                # Ensure any pending tracker operations are committed
                if hasattr(self.tracker, '_save_download_history'):
                    self.tracker._save_download_history()
            except Exception as e:
                logging.error(f"Error saving tracker data: {str(e)}")
        
        # Emit completion signal
        self.download_completed.emit(success, message)
        
    def cancel_download(self):
        """Cancel the download process."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.status_label.setText("Cancelling download...")
            self.cancel_button.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.worker_thread and self.worker_thread.isRunning():
            confirm = QMessageBox.question(
                self,
                "Confirm Cancel",
                "Download is in progress. Cancel the download?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.worker_thread.cancel()
                self.worker_thread.wait(1000)  # Wait for thread to finish
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()