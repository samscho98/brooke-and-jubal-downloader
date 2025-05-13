"""
Audio player module for playing audio files.
"""
import os
import logging
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, QUrl, QTimer, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class AudioPlayer(QObject):
    """Audio player for playing sound files."""
    
    # Signals
    track_started = pyqtSignal(str)  # Emits video_id when track starts
    track_ended = pyqtSignal()       # Emits when track ends
    position_changed = pyqtSignal(int)  # Emits position in milliseconds
    duration_changed = pyqtSignal(int)  # Emits duration in milliseconds
    state_changed = pyqtSignal(int)     # Emits player state
    
    # Player states
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2
    
    def __init__(self):
        """Initialize the audio player."""
        super().__init__()
        
        # Create media player
        self.player = QMediaPlayer()
        
        # Connect signals
        self.player.positionChanged.connect(self.handle_position_changed)
        self.player.durationChanged.connect(self.handle_duration_changed)
        self.player.stateChanged.connect(self.handle_state_changed)
        self.player.mediaStatusChanged.connect(self.handle_media_status_changed)
        
        # Track info
        self.current_track = None
        self.current_track_id = None
        self.current_volume = 80  # Default volume (0-100)
        
        # Initialize with volume
        self.player.setVolume(self.current_volume)
        
        # Timer for track end detection (workaround for some platforms)
        self.track_end_timer = QTimer(self)
        self.track_end_timer.timeout.connect(self.check_track_end)
        self.track_end_timer.setInterval(500)  # Check every 500ms
        
        logging.info("Audio player initialized")
        
    def load(self, file_path: str, track_id: Optional[str] = None) -> bool:
        """
        Load an audio file for playback.
        
        Args:
            file_path: Path to the audio file
            track_id: Optional ID to identify the track
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return False
            
        # Stop current playback
        self.stop()
        
        # Set up new media content
        url = QUrl.fromLocalFile(file_path)
        media = QMediaContent(url)
        self.player.setMedia(media)
        
        # Set volume
        self.player.setVolume(self.current_volume)
        
        # Store track info
        self.current_track = file_path
        self.current_track_id = track_id
        
        logging.info(f"Loaded audio file: {file_path}")
        return True
        
    def play(self) -> None:
        """Start or resume playback."""
        logging.info("Playing audio")
        self.player.play()
        
        # Start monitoring for track end
        if not self.track_end_timer.isActive():
            self.track_end_timer.start()
            
    def pause(self) -> None:
        """Pause playback."""
        logging.info("Pausing audio")
        self.player.pause()
        
    def stop(self) -> None:
        """Stop playback."""
        logging.info("Stopping audio")
        self.player.stop()
        
        # Stop monitoring for track end
        if self.track_end_timer.isActive():
            self.track_end_timer.stop()
        
    def set_position(self, position_ms: int) -> None:
        """
        Set the playback position.
        
        Args:
            position_ms: Position in milliseconds
        """
        logging.debug(f"Setting position to {position_ms}ms")
        self.player.setPosition(position_ms)
        
    def set_position_and_play(self, position_ms: int) -> None:
        """
        Set the playback position and start playing.
        
        Args:
            position_ms: Position in milliseconds
        """
        self.set_position(position_ms)
        self.play()
        
    def set_volume(self, volume: int) -> None:
        """
        Set the player volume.
        
        Args:
            volume: Volume level (0-100)
        """
        # Ensure volume is within range
        volume = max(0, min(100, volume))
        
        logging.debug(f"Setting volume to {volume}")
        self.current_volume = volume
        self.player.setVolume(volume)
        
    def get_position(self) -> int:
        """
        Get the current playback position.
        
        Returns:
            Current position in milliseconds
        """
        return self.player.position()
        
    def get_duration(self) -> int:
        """
        Get the duration of the current track.
        
        Returns:
            Duration in milliseconds
        """
        return self.player.duration()
        
    def get_state(self) -> int:
        """
        Get the current player state.
        
        Returns:
            Player state (STOPPED, PLAYING, PAUSED)
        """
        # Map QMediaPlayer states to our constants
        state = self.player.state()
        if state == QMediaPlayer.StoppedState:
            return self.STOPPED
        elif state == QMediaPlayer.PlayingState:
            return self.PLAYING
        elif state == QMediaPlayer.PausedState:
            return self.PAUSED
        return self.STOPPED
        
    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return self.get_state() == self.PLAYING
    
    def handle_position_changed(self, position: int) -> None:
        """
        Handle position change signal from the player.
        
        Args:
            position: Current position in milliseconds
        """
        self.position_changed.emit(position)
        
    def handle_duration_changed(self, duration: int) -> None:
        """
        Handle duration change signal from the player.
        
        Args:
            duration: Duration in milliseconds
        """
        logging.debug(f"Media duration: {duration}ms")
        self.duration_changed.emit(duration)
        
    def handle_state_changed(self, state: int) -> None:
        """
        Handle state change signal from the player.
        
        Args:
            state: QMediaPlayer state value
        """
        # Map QMediaPlayer states to our constants
        if state == QMediaPlayer.StoppedState:
            mapped_state = self.STOPPED
        elif state == QMediaPlayer.PlayingState:
            mapped_state = self.PLAYING
        elif state == QMediaPlayer.PausedState:
            mapped_state = self.PAUSED
        else:
            mapped_state = self.STOPPED
            
        logging.debug(f"Player state changed to: {mapped_state}")
        self.state_changed.emit(mapped_state)
        
    def handle_media_status_changed(self, status: int) -> None:
        """
        Handle media status change signal from the player.
        
        Args:
            status: QMediaPlayer media status value
        """
        # Check for track start and end events
        if status == QMediaPlayer.LoadedMedia:
            logging.debug("Media loaded")
        elif status == QMediaPlayer.LoadingMedia:
            logging.debug("Media loading")
        elif status == QMediaPlayer.BufferingMedia:
            logging.debug("Media buffering")
        elif status == QMediaPlayer.BufferedMedia:
            # This often indicates the media is ready to play
            logging.debug("Media buffered")
            if self.current_track_id:
                self.track_started.emit(self.current_track_id)
        elif status == QMediaPlayer.EndOfMedia:
            logging.debug("Media ended")
            self.stop()
            self.track_ended.emit()
        elif status == QMediaPlayer.InvalidMedia:
            logging.error("Invalid media")
            self.stop()
            
    def check_track_end(self) -> None:
        """
        Check if the track has ended. This is a workaround for platforms
        where the EndOfMedia status might not be reliable.
        """
        # Only check if we're playing and we have a track
        if self.get_state() == self.PLAYING and self.current_track:
            position = self.get_position()
            duration = self.get_duration()
            
            # Check if we're at the end of the track
            # Use a small threshold to account for timing issues
            if position >= duration - 200 and duration > 0:
                logging.debug("Track end detected by timer")
                self.stop()
                self.track_ended.emit()