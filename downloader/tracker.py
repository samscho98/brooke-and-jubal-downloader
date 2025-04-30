"""
Download tracker module.
Keeps track of downloaded files and maintains the collection up to date.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DownloadTracker:
    """Class to track downloaded videos and maintain the collection state."""
    
    def __init__(self, history_file: str = "download_history.json", 
                playlists_file: str = "playlists.json"):
        """
        Initialize the download tracker.
        
        Args:
            history_file: Path to the file storing download history
            playlists_file: Path to the file storing playlist information
        """
        self.history_file = history_file
        self.playlists_file = playlists_file
        self.download_history = self._load_download_history()
        self.playlists = self._load_playlists()
        
    def _load_download_history(self) -> Dict:
        """
        Load the download history from file.
        
        Returns:
            Dictionary containing the download history
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {self.history_file}. Creating new history.")
                return {"videos": {}, "last_updated": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Error loading download history: {str(e)}")
                return {"videos": {}, "last_updated": datetime.now().isoformat()}
        else:
            logger.info(f"Download history file not found. Creating new history.")
            return {"videos": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_download_history(self) -> bool:
        """
        Save the download history to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the last_updated timestamp
            self.download_history["last_updated"] = datetime.now().isoformat()
            
            # Save to file with pretty printing
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved download history to {self.history_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving download history: {str(e)}")
            return False
    
    def _load_playlists(self) -> Dict:
        """
        Load the playlists configuration from file.
        
        Returns:
            Dictionary containing the playlists configuration
        """
        if os.path.exists(self.playlists_file):
            try:
                with open(self.playlists_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {self.playlists_file}. Creating new playlists file.")
                return {"playlists": []}
            except Exception as e:
                logger.error(f"Error loading playlists: {str(e)}")
                return {"playlists": []}
        else:
            logger.info(f"Playlists file not found. Creating new playlists file.")
            return {"playlists": []}
    
    def _save_playlists(self) -> bool:
        """
        Save the playlists configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save to file with pretty printing
            with open(self.playlists_file, 'w', encoding='utf-8') as f:
                json.dump(self.playlists, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved playlists to {self.playlists_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving playlists: {str(e)}")
            return False
    
    def add_playlist(self, url: str, name: str = None, check_interval: int = 24) -> bool:
        """
        Add a new playlist to track.
        
        Args:
            url: URL of the playlist
            name: Optional name for the playlist
            check_interval: How often to check for updates (in hours)
            
        Returns:
            True if added successfully, False otherwise
        """
        # Generate a default name if none provided
        if name is None:
            name = f"Playlist {len(self.playlists['playlists']) + 1}"
        
        # Check if playlist already exists
        for playlist in self.playlists["playlists"]:
            if playlist["url"] == url:
                logger.warning(f"Playlist {url} already exists.")
                return False
        
        # Add the playlist
        playlist_info = {
            "name": name,
            "url": url,
            "check_interval": check_interval,
            "last_checked": None,
            "added_on": datetime.now().isoformat()
        }
        
        self.playlists["playlists"].append(playlist_info)
        return self._save_playlists()
    
    def remove_playlist(self, url: str) -> bool:
        """
        Remove a playlist from tracking.
        
        Args:
            url: URL of the playlist to remove
            
        Returns:
            True if removed successfully, False if not found
        """
        initial_count = len(self.playlists["playlists"])
        self.playlists["playlists"] = [p for p in self.playlists["playlists"] if p["url"] != url]
        
        if len(self.playlists["playlists"]) < initial_count:
            logger.info(f"Removed playlist: {url}")
            return self._save_playlists()
        else:
            logger.warning(f"Playlist not found: {url}")
            return False
    
    def get_playlists(self) -> List[Dict]:
        """
        Get all tracked playlists.
        
        Returns:
            List of playlist dictionaries
        """
        return self.playlists["playlists"]
    
    def update_playlist_check_time(self, url: str) -> bool:
        """
        Update the last checked time for a playlist.
        
        Args:
            url: URL of the playlist
            
        Returns:
            True if updated successfully, False if not found
        """
        for playlist in self.playlists["playlists"]:
            if playlist["url"] == url:
                playlist["last_checked"] = datetime.now().isoformat()
                return self._save_playlists()
        
        logger.warning(f"Playlist not found: {url}")
        return False
    
    def add_downloaded_video(self, video_id: str, playlist_id: str, 
                           title: str, file_path: str) -> bool:
        """
        Add a downloaded video to the history.
        
        Args:
            video_id: YouTube video ID
            playlist_id: YouTube playlist ID
            title: Title of the video
            file_path: Path to the downloaded file
            
        Returns:
            True if added successfully, False otherwise
        """
        if video_id in self.download_history["videos"]:
            # Update existing record
            self.download_history["videos"][video_id]["playlists"].append(playlist_id)
            self.download_history["videos"][video_id]["playlists"] = list(set(
                self.download_history["videos"][video_id]["playlists"]
            ))
            self.download_history["videos"][video_id]["last_updated"] = datetime.now().isoformat()
        else:
            # Create new record
            self.download_history["videos"][video_id] = {
                "title": title,
                "file_path": file_path,
                "playlists": [playlist_id],
                "downloaded_on": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        
        return self._save_download_history()
    
    def is_video_downloaded(self, video_id: str) -> bool:
        """
        Check if a video has already been downloaded.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if the video is already downloaded, False otherwise
        """
        return video_id in self.download_history["videos"]
    
    def get_downloaded_videos(self, playlist_id: Optional[str] = None) -> List[Dict]:
        """
        Get all downloaded videos, optionally filtered by playlist.
        
        Args:
            playlist_id: Optional YouTube playlist ID to filter by
            
        Returns:
            List of video dictionaries
        """
        videos = []
        
        for video_id, video_info in self.download_history["videos"].items():
            if playlist_id is None or playlist_id in video_info["playlists"]:
                video_data = {
                    "id": video_id,
                    "title": video_info["title"],
                    "file_path": video_info["file_path"],
                    "downloaded_on": video_info["downloaded_on"]
                }
                videos.append(video_data)
        
        return videos
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check which playlists need to be updated based on their check interval.
        
        Returns:
            List of playlists that need to be updated
        """
        now = datetime.now()
        playlists_to_update = []
        
        for playlist in self.playlists["playlists"]:
            # Always update if never checked before
            if playlist["last_checked"] is None:
                playlists_to_update.append(playlist)
                continue
            
            # Calculate time difference
            last_checked = datetime.fromisoformat(playlist["last_checked"])
            hours_diff = (now - last_checked).total_seconds() / 3600
            
            if hours_diff >= playlist["check_interval"]:
                playlists_to_update.append(playlist)
        
        return playlists_to_update