"""
Audio player module.
"""
import os
import logging
from typing import Optional, Dict, Callable

from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QTime
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudio

class AudioPlayer(QObject):
    """Audio player component with signals for UI integration."""
    
    # Signals
    track_started = pyqtSignal(str)  # Track ID
    track_ended = pyqtSignal()
    track_paused = pyqtSignal()
    track_resumed = pyqtSignal()
    position_changed = pyqtSignal(int)  # Position in milliseconds
    duration_changed = pyqtSignal(int)  # Duration in milliseconds
    volume_changed = pyqtSignal(int)    # Volume as percentage (0-100)
    error_occurred = pyqtSignal(str)    # Error message
    
    def __init__(self):
        """Initialize the audio player."""
        super().__init__()
        self.player = QMediaPlayer()
        self.current_track_id = None
        self.current_file_path = None
        self.volume = 80  # Default volume 80%
        
        # Connect signals
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.stateChanged.connect(self._on_state_changed)
        self.player.error.connect(self._on_error)
        
        # Set initial volume
        self.set_volume(self.volume)
    
    def load(self, file_path: str, track_id: Optional[str] = None) -> bool:
        """
        Load an audio file for playback.
        
        Args:
            file_path: Path to the audio file
            track_id: Optional ID to identify the track
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            self.error_occurred.emit(f"File not found: {file_path}")
            return False
        
        try:
            # Create a QUrl from the file path
            url = QUrl.fromLocalFile(file_path)
            content = QMediaContent(url)
            
            # Load the media
            self.player.setMedia(content)
            
            # Store track info
            self.current_track_id = track_id
            self.current_file_path = file_path
            
            logging.info(f"Loaded audio file: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading audio file: {str(e)}")
            self.error_occurred.emit(f"Error loading file: {str(e)}")
            return False
    
    def play(self):
        """Start or resume playback."""
        self.player.play()
    
    def pause(self):
        """Pause playback."""
        self.player.pause()
    
    def stop(self):
        """Stop playback."""
        self.player.stop()
    
    def seek(self, position_ms: int):
        """
        Seek to a specific position.
        
        Args:
            position_ms: Position in milliseconds
        """
        self.player.setPosition(position_ms)
    
    def set_position(self, position_ms: int):
        """
        Set the playback position without playing.
        
        Args:
            position_ms: Position in milliseconds
        """
        self.player.setPosition(position_ms)
    
    def set_position_and_play(self, position_ms: int):
        """
        Set the playback position and start playing.
        
        Args:
            position_ms: Position in milliseconds
        """
        self.player.setPosition(position_ms)
        self.player.play()
    
    def set_volume(self, volume: int):
        """
        Set the playback volume.
        
        Args:
            volume: Volume as percentage (0-100)
        """
        # QMediaPlayer volume is from 0-100, matches our percentage
        self.player.setVolume(volume)
        self.volume = volume
        self.volume_changed.emit(volume)
    
    def get_position(self) -> int:
        """
        Get the current position in milliseconds.
        
        Returns:
            Current position in milliseconds
        """
        return self.player.position()
    
    def get_duration(self) -> int:
        """
        Get the total duration in milliseconds.
        
        Returns:
            Total duration in milliseconds
        """
        return self.player.duration()
    
    def is_playing(self) -> bool:
        """
        Check if the player is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return self.player.state() == QMediaPlayer.PlayingState
    
    def get_current_track_id(self) -> Optional[str]:
        """
        Get the ID of the currently loaded track.
        
        Returns:
            Track ID or None if no track is loaded
        """
        return self.current_track_id
    
    def format_position(self) -> str:
        """
        Format the current position as MM:SS.
        
        Returns:
            Formatted position string
        """
        position = self.player.position()
        time = QTime(0, 0)
        time = time.addMSecs(position)
        return time.toString("mm:ss")
    
    def format_duration(self) -> str:
        """
        Format the total duration as MM:SS.
        
        Returns:
            Formatted duration string
        """
        duration = self.player.duration()
        time = QTime(0, 0)
        time = time.addMSecs(duration)
        return time.toString("mm:ss")
    
    def _on_media_status_changed(self, status):
        """
        Handle media status changes.
        
        Args:
            status: The new media status
        """
        if status == QMediaPlayer.LoadedMedia:
            logging.info(f"Media loaded: {self.current_file_path}")
            
        elif status == QMediaPlayer.EndOfMedia:
            logging.info(f"Media playback ended: {self.current_file_path}")
            self.track_ended.emit()
            
        elif status == QMediaPlayer.InvalidMedia:
            logging.error(f"Invalid media: {self.current_file_path}")
            self.error_occurred.emit(f"Invalid media: {self.current_file_path}")
    
    def _on_position_changed(self, position):
        """
        Handle position changes.
        
        Args:
            position: New position in milliseconds
        """
        self.position_changed.emit(position)
    
    def _on_duration_changed(self, duration):
        """
        Handle duration changes.
        
        Args:
            duration: Duration in milliseconds
        """
        self.duration_changed.emit(duration)
    
    def _on_state_changed(self, state):
        """
        Handle player state changes.
        
        Args:
            state: The new player state
        """
        if state == QMediaPlayer.PlayingState:
            if self.current_track_id:
                self.track_started.emit(self.current_track_id)
            self.track_resumed.emit()
            logging.info(f"Started playback: {self.current_file_path}")
            
        elif state == QMediaPlayer.PausedState:
            self.track_paused.emit()
            logging.info(f"Paused playback: {self.current_file_path}")
            
        elif state == QMediaPlayer.StoppedState:
            logging.info(f"Stopped playback: {self.current_file_path}")
    
    def _on_error(self, error):
        """
        Handle player errors.
        
        Args:
            error: The error code
        """
        error_msg = f"Player error: {self.player.errorString()}"
        logging.error(error_msg)
        self.error_occurred.emit(error_msg)