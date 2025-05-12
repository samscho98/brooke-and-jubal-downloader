"""
Score calculator for determining audio playback order.
"""
import os
import json
import math
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional, Any

class ScoreCalculator:
    """
    Simplified score calculator for determining optimal audio playback order.
    Uses placeholder scores for initial implementation.
    """
    
    def __init__(self, scores_file: str = "data/video_scores.json"):
        """
        Initialize the score calculator.
        
        Args:
            scores_file: Path to JSON file for storing score data
        """
        self.scores_file = scores_file
        self.scores_data = self._load_scores()
        
        # Define time slots for different parts of the day
        self.TIME_SLOTS = {
            "morning": (5, 11),      # 5:00 AM - 11:59 AM
            "afternoon": (12, 16),   # 12:00 PM - 4:59 PM
            "evening": (17, 21),     # 5:00 PM - 9:59 PM
            "night": (22, 4)         # 10:00 PM - 4:59 AM
        }
    
    def _load_scores(self) -> Dict:
        """
        Load scores from file or create default if not exists.
        
        Returns:
            Scores data dictionary
        """
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading scores file: {str(e)}")
                return self._create_default_scores()
        else:
            return self._create_default_scores()
    
    def _create_default_scores(self) -> Dict:
        """
        Create default scores structure.
        
        Returns:
            Default scores data dictionary
        """
        default_data = {
            "videos": {},
            "user_preferences": {
                "time_effect_strength": 1.0,
                "new_content_boost": 1.5,
                "score_decay": 0.9
            },
            "play_history": [],
            "last_updated": datetime.now().isoformat()
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.scores_file), exist_ok=True)
        
        # Save default data
        with open(self.scores_file, 'w') as f:
            json.dump(default_data, f, indent=2)
            
        return default_data
    
    def _save_scores(self):
        """Save scores data to file."""
        try:
            # Update last updated timestamp
            self.scores_data["last_updated"] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.scores_file), exist_ok=True)
            
            # Save data
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores_data, f, indent=2)
                
            logging.info(f"Scores saved to {self.scores_file}")
            
        except Exception as e:
            logging.error(f"Error saving scores file: {str(e)}")
    
    def get_current_time_slot(self) -> str:
        """
        Get the current time slot based on the time of day.
        
        Returns:
            Current time slot name
        """
        current_hour = datetime.now().hour
        
        for slot_name, (start, end) in self.TIME_SLOTS.items():
            if start <= end:
                # Normal time range (e.g., 5-11)
                if start <= current_hour <= end:
                    return slot_name
            else:
                # Overnight time range (e.g., 22-4)
                if current_hour >= start or current_hour <= end:
                    return slot_name
        
        # Default fallback
        return "afternoon"
    
    def calculate_score(self, video_id: str, video_data: Dict = None) -> float:
        """
        Calculate a placeholder score for a video.
        
        Args:
            video_id: Video ID
            video_data: Optional video data
            
        Returns:
            Score value
        """
        # Get video from scores data or use provided data
        if video_id in self.scores_data["videos"]:
            video_info = self.scores_data["videos"][video_id]
        elif video_data:
            # Initialize with provided data
            video_info = {
                "youtube_views": video_data.get("view_count", 0),
                "youtube_comments": video_data.get("comment_count", 0),
                "upload_date": video_data.get("upload_date", ""),
                "duration_seconds": video_data.get("duration_seconds", 0),
                "title": video_data.get("title", "Unknown"),
                "play_count": 0,
                "last_played": None
            }
            self.scores_data["videos"][video_id] = video_info
            self._save_scores()
        else:
            # No data available
            return 0.0
        
        # Simple placeholder scoring logic
        view_count = video_info.get("youtube_views", 0)
        
        # Base score using logarithmic scale for views
        base_score = math.log10(max(100, view_count)) * 2
        
        # Add some randomness to make playlists more interesting
        randomness = random.uniform(0.8, 1.2)
        
        # Apply time of day effect
        time_slot = self.get_current_time_slot()
        time_multiplier = 1.0
        
        # Placeholder logic: boost evening/night content slightly
        if time_slot == "evening":
            time_multiplier = 1.1
        elif time_slot == "night":
            time_multiplier = 1.2
            
        # Calculate final score
        final_score = base_score * randomness * time_multiplier
        
        return final_score
    
    def get_top_videos(self, videos: List[Dict] = None, time_slot: str = None, limit: int = 10) -> List[Dict]:
        """
        Get top videos sorted by score.
        
        Args:
            videos: Optional list of videos to score and sort
            time_slot: Optional time slot to use (defaults to current)
            limit: Maximum number of videos to return
            
        Returns:
            List of videos with scores, sorted by score in descending order
        """
        if time_slot is None:
            time_slot = self.get_current_time_slot()
        
        scored_videos = []
        
        # If videos provided, score those
        if videos:
            for video in videos:
                video_id = video.get("id")
                if video_id:
                    score = self.calculate_score(video_id, video)
                    video_copy = video.copy()
                    video_copy["score"] = score
                    video_copy["is_new_release"] = False  # Placeholder
                    scored_videos.append(video_copy)
        else:
            # Use videos from tracker
            from downloader.tracker import DownloadTracker
            tracker = DownloadTracker()
            downloaded_videos = tracker.get_downloaded_videos()
            
            for video in downloaded_videos:
                video_id = video.get("id")
                if video_id:
                    score = self.calculate_score(video_id, video)
                    video_copy = video.copy()
                    video_copy["score"] = score
                    
                    # Compute base score and engagement score for display
                    view_count = video.get("view_count", 0)
                    video_copy["base_score"] = math.log10(max(100, view_count))
                    video_copy["engagement_score"] = score - video_copy["base_score"]
                    video_copy["youtube_views"] = view_count
                    
                    # Check if it's a new video (placeholder logic)
                    video_copy["is_new_release"] = random.random() < 0.1  # 10% chance to mark as new
                    
                    scored_videos.append(video_copy)
        
        # Sort by score (descending)
        scored_videos.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Limit results
        return scored_videos[:limit]
    
    def record_play(self, video_id: str, duration_played: int = None):
        """
        Record that a video was played.
        
        Args:
            video_id: Video ID that was played
            duration_played: Optional duration played in seconds
        """
        if video_id not in self.scores_data["videos"]:
            return
            
        # Update video play count and last played time
        self.scores_data["videos"][video_id]["play_count"] = self.scores_data["videos"][video_id].get("play_count", 0) + 1
        self.scores_data["videos"][video_id]["last_played"] = datetime.now().isoformat()
        
        # Add to play history
        self.scores_data["play_history"].append({
            "video_id": video_id,
            "timestamp": datetime.now().isoformat(),
            "duration_played": duration_played
        })
        
        # Trim history if it gets too long
        if len(self.scores_data["play_history"]) > 1000:
            self.scores_data["play_history"] = self.scores_data["play_history"][-1000:]
            
        self._save_scores()