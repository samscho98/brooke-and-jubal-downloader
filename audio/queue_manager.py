"""
Queue manager for audio playback.
"""
import os
import json
import logging
import random
from typing import List, Dict, Optional, Any
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class QueueManager(QObject):
    """Manages audio playback queues."""
    
    # Signals
    queue_updated = pyqtSignal(list)  # Emitted when the queue is updated
    
    def __init__(self, history_file: str = "data/play_history.json"):
        """
        Initialize the queue manager.
        
        Args:
            history_file: Path to the file storing playback history
        """
        super().__init__()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        self.history_file = history_file
        self.current_queue = []
        self.current_index = -1
        self.play_history = []
        
        # Load history
        self._load_history()
        
        logging.debug("QueueManager initialized")
    
    def _load_history(self):
        """Load playback history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.play_history = data.get('history', [])
                    logging.debug(f"Loaded {len(self.play_history)} entries from play history")
            else:
                # Create empty history file
                self._save_history()
        except Exception as e:
            logging.error(f"Error loading play history: {str(e)}")
            self.play_history = []
    
    def _save_history(self):
        """Save playback history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.play_history,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
            logging.debug(f"Saved {len(self.play_history)} entries to play history")
        except Exception as e:
            logging.error(f"Error saving play history: {str(e)}")
    
    def set_queue(self, tracks: List[Dict[str, Any]]):
        """
        Set the current queue.
        
        Args:
            tracks: List of track dictionaries (must have 'id' field)
        """
        if not tracks:
            logging.warning("Attempted to set empty queue")
            return
            
        self.current_queue = tracks
        self.current_index = -1
        self.queue_updated.emit(self.current_queue)
        logging.info(f"Queue set with {len(tracks)} tracks")
    
    def add_to_queue(self, track: Dict[str, Any], position: Optional[int] = None):
        """
        Add a track to the queue.
        
        Args:
            track: Track dictionary (must have 'id' field)
            position: Position to insert the track (None for end of queue)
        """
        if not track or 'id' not in track:
            logging.warning("Attempted to add invalid track to queue")
            return
            
        if position is not None and 0 <= position <= len(self.current_queue):
            self.current_queue.insert(position, track)
            # Update current_index if the track was inserted before the current track
            if position <= self.current_index:
                self.current_index += 1
        else:
            self.current_queue.append(track)
            
        self.queue_updated.emit(self.current_queue)
        logging.debug(f"Added track {track.get('title', track['id'])} to queue")
    
    def remove_from_queue(self, index: int):
        """
        Remove a track from the queue.
        
        Args:
            index: Index of track to remove
        """
        if not 0 <= index < len(self.current_queue):
            logging.warning(f"Attempted to remove invalid track index: {index}")
            return
            
        removed_track = self.current_queue.pop(index)
        
        # Update current_index if the removed track was before the current track
        if index < self.current_index:
            self.current_index -= 1
        # Reset current_index if the current track was removed
        elif index == self.current_index:
            self.current_index = -1
            
        self.queue_updated.emit(self.current_queue)
        logging.debug(f"Removed track {removed_track.get('title', removed_track.get('id'))} from queue")
    
    def clear_queue(self):
        """Clear the current queue."""
        self.current_queue = []
        self.current_index = -1
        self.queue_updated.emit(self.current_queue)
        logging.info("Queue cleared")
    
    def get_queue(self) -> List[Dict[str, Any]]:
        """
        Get the current queue.
        
        Returns:
            List of track dictionaries
        """
        return self.current_queue
    
    def get_current_track(self) -> Optional[Dict[str, Any]]:
        """
        Get the current track.
        
        Returns:
            Current track dictionary or None if no track is selected
        """
        if 0 <= self.current_index < len(self.current_queue):
            return self.current_queue[self.current_index]
        return None
    
    def get_next_track(self) -> Optional[Dict[str, Any]]:
        """
        Get the next track in the queue.
        
        Returns:
            Next track dictionary or None if at the end of the queue
        """
        next_index = self.current_index + 1
        if next_index < len(self.current_queue):
            return self.current_queue[next_index]
        return None
    
    def get_previous_track(self) -> Optional[Dict[str, Any]]:
        """
        Get the previous track in the queue.
        
        Returns:
            Previous track dictionary or None if at the beginning of the queue
        """
        prev_index = self.current_index - 1
        if prev_index >= 0:
            return self.current_queue[prev_index]
        return None
    
    def advance_queue(self) -> Optional[Dict[str, Any]]:
        """
        Advance to the next track in the queue.
        
        Returns:
            Next track dictionary or None if at the end of the queue
        """
        next_index = self.current_index + 1
        if next_index < len(self.current_queue):
            self.current_index = next_index
            track = self.current_queue[self.current_index]
            self._add_to_history(track)
            return track
        return None
    
    def go_to_previous(self) -> Optional[Dict[str, Any]]:
        """
        Go to the previous track in the queue.
        
        Returns:
            Previous track dictionary or None if at the beginning of the queue
        """
        prev_index = self.current_index - 1
        if prev_index >= 0:
            self.current_index = prev_index
            track = self.current_queue[self.current_index]
            return track
        return None
    
    def set_current_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Set the current track by index.
        
        Args:
            index: Index of track to set as current
            
        Returns:
            Track dictionary or None if index is invalid
        """
        if 0 <= index < len(self.current_queue):
            self.current_index = index
            track = self.current_queue[self.current_index]
            self._add_to_history(track)
            return track
            
        logging.warning(f"Attempted to set invalid current index: {index}")
        return None
    
    def shuffle_queue(self, maintain_current: bool = True):
        """
        Shuffle the queue.
        
        Args:
            maintain_current: If True, keep the current track in its position
        """
        if not self.current_queue:
            return
            
        current_track = self.get_current_track()
        
        if maintain_current and current_track:
            # Remove current track, shuffle the rest, then reinsert
            remaining_tracks = self.current_queue[:self.current_index] + self.current_queue[self.current_index+1:]
            random.shuffle(remaining_tracks)
            
            self.current_queue = remaining_tracks[:self.current_index] + [current_track] + remaining_tracks[self.current_index:]
        else:
            # Shuffle the entire queue
            random.shuffle(self.current_queue)
            self.current_index = -1
            
        self.queue_updated.emit(self.current_queue)
        logging.info("Queue shuffled")
    
    def _add_to_history(self, track: Dict[str, Any]):
        """
        Add a track to the play history.
        
        Args:
            track: Track dictionary
        """
        if not track:
            return
            
        # Create history entry
        entry = {
            'track_id': track.get('id'),
            'title': track.get('title', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'position': self.current_index
        }
        
        # Add to history
        self.play_history.append(entry)
        
        # Trim history if too long (keep last 1000 entries)
        if len(self.play_history) > 1000:
            self.play_history = self.play_history[-1000:]
            
        # Save history
        self._save_history()
        
        logging.debug(f"Added track {track.get('title', track.get('id'))} to play history")
    
    def get_play_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the play history.
        
        Args:
            limit: Maximum number of entries to return (None for all)
            
        Returns:
            List of history entries (most recent first)
        """
        if limit is not None and limit > 0:
            return self.play_history[-limit:]
        return self.play_history.copy()
    
    def clear_history(self):
        """Clear the play history."""
        self.play_history = []
        self._save_history()
        logging.info("Play history cleared")