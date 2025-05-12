"""
Scoring system module.
Handles calculating and tracking performance scores for audio files.
"""
import os
import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ScoringSystem:
    """Class to handle video scoring and performance tracking."""
    
    def __init__(self, scores_file: str = "data/video_scores.json"):
        """
        Initialize the scoring system.
        
        Args:
            scores_file: Path to the file storing video scores
        """
        self.scores_file = scores_file
        self.scores_data = self._load_scores()
        
    def _load_scores(self) -> Dict:
        """
        Load the scores from file.
        
        Returns:
            Dictionary containing the scores data
        """
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {self.scores_file}. Creating new scores file.")
                return self._create_default_scores()
            except Exception as e:
                logger.error(f"Error loading scores: {str(e)}")
                return self._create_default_scores()
        else:
            logger.info(f"Scores file not found. Creating new scores file.")
            return self._create_default_scores()
    
    def _create_default_scores(self) -> Dict:
        """Create a default scores structure."""
        return {
            "videos": {},
            "time_slots": {
                "US_PrimeTime": {
                    "start_time": "22:00",
                    "end_time": "03:00",
                    "performance_factor": 1.3
                },
                "UK_Evening": {
                    "start_time": "18:00",
                    "end_time": "22:00",
                    "performance_factor": 1.1
                },
                "PH_Evening": {
                    "start_time": "10:00",
                    "end_time": "16:00",
                    "performance_factor": 0.9
                },
                "Low_Traffic": {
                    "start_time": "03:00",
                    "end_time": "10:00",
                    "performance_factor": 0.7
                }
            },
            "playlists": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_scores(self) -> bool:
        """
        Save the scores to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the last_updated timestamp
            self.scores_data["last_updated"] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.scores_file), exist_ok=True)
            
            # Save to file with pretty printing
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved scores to {self.scores_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving scores: {str(e)}")
            return False
    
    def update_video_metadata(self, video_id: str, title: str, youtube_views: int, 
                             youtube_comments: int, upload_date: Optional[str] = None,
                             is_new_release: bool = False) -> bool:
        """
        Update basic metadata for a video and recalculate its base score.
        
        Args:
            video_id: YouTube video ID
            title: Video title
            youtube_views: Number of views on YouTube
            youtube_comments: Number of comments on YouTube
            upload_date: Optional upload date (YYYYMMDD format)
            is_new_release: Whether this is a new release (< 14 days)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if video_id not in self.scores_data["videos"]:
                # Create new video entry
                self.scores_data["videos"][video_id] = {
                    "title": title,
                    "youtube_views": youtube_views,
                    "youtube_comments": youtube_comments,
                    "view_count_updated": datetime.now().isoformat(),
                    "stream_metrics": {
                        "stream_chat_messages": 0,
                        "viewer_change": 0,
                        "avg_viewers_during_segment": 0,
                        "returning_viewer_count": 0,
                        "returning_viewer_percentage": 0,
                        "returning_viewer_retention": 0,
                        "times_played": 0
                    },
                    "scores": {},
                    "time_effects": {
                        "US_PrimeTime": 1.3,
                        "UK_Evening": 1.1,
                        "PH_Evening": 0.9,
                        "Low_Traffic": 0.7
                    },
                    "history": []
                }
                
                if upload_date:
                    self.scores_data["videos"][video_id]["upload_date"] = upload_date
                    
                    # Calculate days since release if upload_date is provided
                    try:
                        upload_dt = datetime.strptime(upload_date, "%Y%m%d")
                        days_since = (datetime.now() - upload_dt).days
                        self.scores_data["videos"][video_id]["days_since_release"] = days_since
                        self.scores_data["videos"][video_id]["is_new_release"] = days_since < 14
                    except ValueError:
                        # If date format is invalid, just use the is_new_release flag
                        self.scores_data["videos"][video_id]["is_new_release"] = is_new_release
            else:
                # Update existing video
                self.scores_data["videos"][video_id]["title"] = title
                self.scores_data["videos"][video_id]["youtube_views"] = youtube_views
                self.scores_data["videos"][video_id]["youtube_comments"] = youtube_comments
                self.scores_data["videos"][video_id]["view_count_updated"] = datetime.now().isoformat()
                
                if upload_date:
                    self.scores_data["videos"][video_id]["upload_date"] = upload_date
                    
                    # Update days since release
                    try:
                        upload_dt = datetime.strptime(upload_date, "%Y%m%d")
                        days_since = (datetime.now() - upload_dt).days
                        self.scores_data["videos"][video_id]["days_since_release"] = days_since
                        self.scores_data["videos"][video_id]["is_new_release"] = days_since < 14
                    except ValueError:
                        pass
            
            # Calculate base score
            self._calculate_base_score(video_id)
            
            return self._save_scores()
            
        except Exception as e:
            logger.error(f"Error updating video metadata: {str(e)}")
            return False
    
    def _calculate_base_score(self, video_id: str) -> float:
        """
        Calculate the base score for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Calculated base score
        """
        try:
            video = self.scores_data["videos"][video_id]
            
            # Get YouTube metrics
            youtube_views = video.get("youtube_views", 0)
            youtube_comments = video.get("youtube_comments", 0)
            
            # Avoid division by zero
            if youtube_views == 0:
                youtube_views = 1
            
            # Calculate engagement boost
            engagement_boost = 1 + (youtube_comments / youtube_views)
            
            # Calculate base score
            base_score = math.log10(max(youtube_views, 1)) * engagement_boost
            
            # Apply special handling for new releases
            is_new_release = video.get("is_new_release", False)
            days_since_release = video.get("days_since_release", 100)
            
            if youtube_views < 10000 and is_new_release:
                # Provide a boost for new content
                min_score = 3.5  # Equivalent to about 3,000+ views
                base_score = max(base_score, min_score)
                
                # Add freshness bonus
                freshness_bonus = (14 - days_since_release) * 0.1  # Up to +1.4 bonus
                base_score += max(0, freshness_bonus)  # Ensure non-negative
            
            # Store the calculated score
            video["scores"]["base_score"] = base_score
            
            # Calculate total score based on base score and any available loyalty metrics
            self._calculate_total_score(video_id)
            
            return base_score
            
        except Exception as e:
            logger.error(f"Error calculating base score: {str(e)}")
            return 0
    
    def _calculate_total_score(self, video_id: str) -> float:
        """
        Calculate the total score for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Calculated total score
        """
        try:
            video = self.scores_data["videos"][video_id]
            scores = video.get("scores", {})
            stream_metrics = video.get("stream_metrics", {})
            
            # Get base score
            base_score = scores.get("base_score", 0)
            
            # Calculate loyalty boost if metrics available
            loyalty_boost = 1.0
            returning_viewer_percentage = stream_metrics.get("returning_viewer_percentage", 0)
            if returning_viewer_percentage > 0:
                loyalty_boost = 1 + (returning_viewer_percentage * 0.5)
                scores["loyalty_score"] = returning_viewer_percentage * 0.5
            
            # Calculate engagement score if played before
            engagement_score = 0
            times_played = stream_metrics.get("times_played", 0)
            if times_played > 0:
                # Get YouTube metrics directly from the video object
                youtube_views = video.get("youtube_views", 1)
                youtube_comments = video.get("youtube_comments", 0)
                
                # Engagement based on chat and viewer change
                chat_engagement = stream_metrics.get("stream_chat_messages", 0) / max(stream_metrics.get("avg_viewers_during_segment", 1), 1)
                viewer_change_factor = max(-1, min(1, stream_metrics.get("viewer_change", 0) / 100))  # Normalize to [-1, 1]
                
                engagement_score = (0.6 * (youtube_comments / max(youtube_views, 1)) + 
                                    0.4 * chat_engagement) * (1 + viewer_change_factor)
                scores["engagement_score"] = engagement_score
            
            # Calculate enhanced base score with loyalty
            enhanced_base_score = base_score * loyalty_boost
            scores["enhanced_base_score"] = enhanced_base_score
            
            # Calculate total score
            total_score = enhanced_base_score + engagement_score
            scores["total_score"] = total_score
            
            # Update scores in the video data
            video["scores"] = scores
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating total score: {str(e)}")
            return 0
    
    def record_stream_performance(self, video_id: str, time_slot: str, 
                                viewer_change: int, chat_messages: int,
                                avg_viewers: int, returning_viewer_count: int,
                                returning_viewer_percentage: float,
                                returning_viewer_retention: float) -> bool:
        """
        Record performance metrics from a livestream play.
        
        Args:
            video_id: YouTube video ID
            time_slot: Time slot label (e.g., "US_PrimeTime")
            viewer_change: Change in viewers during playback
            chat_messages: Number of chat messages during playback
            avg_viewers: Average number of viewers during playback
            returning_viewer_count: Number of viewers who have watched previous streams
            returning_viewer_percentage: Percentage of total viewers who are returning
            returning_viewer_retention: Percentage of returning viewers who stay
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if video_id not in self.scores_data["videos"]:
                logger.warning(f"Video {video_id} not found in scores data.")
                return False
            
            video = self.scores_data["videos"][video_id]
            
            # Update stream metrics
            stream_metrics = video.get("stream_metrics", {})
            stream_metrics["viewer_change"] = viewer_change
            stream_metrics["stream_chat_messages"] = chat_messages
            stream_metrics["avg_viewers_during_segment"] = avg_viewers
            stream_metrics["returning_viewer_count"] = returning_viewer_count
            stream_metrics["returning_viewer_percentage"] = returning_viewer_percentage
            stream_metrics["returning_viewer_retention"] = returning_viewer_retention
            stream_metrics["times_played"] = stream_metrics.get("times_played", 0) + 1
            
            video["stream_metrics"] = stream_metrics
            
            # Add play history
            history_entry = {
                "played_at": datetime.now().isoformat(),
                "time_slot": time_slot,
                "viewer_change": viewer_change,
                "chat_messages": chat_messages,
                "returning_viewer_percentage": returning_viewer_percentage
            }
            
            if "history" not in video:
                video["history"] = []
            
            video["history"].append(history_entry)
            
            # Recalculate scores
            self._calculate_total_score(video_id)
            
            return self._save_scores()
            
        except Exception as e:
            logger.error(f"Error recording stream performance: {str(e)}")
            return False
    
    def get_top_videos(self, time_slot: Optional[str] = None, 
                     playlist_id: Optional[str] = None,
                     limit: int = 10,
                     include_new_releases: bool = True) -> List[Dict]:
        """
        Get top scoring videos, optionally filtered by time slot or playlist.
        
        Args:
            time_slot: Optional time slot to filter by
            playlist_id: Optional playlist ID to filter by
            limit: Maximum number of videos to return
            include_new_releases: Whether to include new releases regardless of score
            
        Returns:
            List of video dictionaries with scores
        """
        videos = []
        
        try:
            # Get all videos
            for video_id, video_data in self.scores_data["videos"].items():
                scores = video_data.get("scores", {})
                
                # Skip videos without scores
                if not scores:
                    continue
                
                # Get the appropriate score based on time slot
                score = scores.get("total_score", 0)
                if time_slot and time_slot in video_data.get("time_effects", {}):
                    # Apply time slot effect
                    score *= video_data["time_effects"][time_slot]
                
                videos.append({
                    "id": video_id,
                    "title": video_data.get("title", "Unknown"),
                    "score": score,
                    "base_score": scores.get("base_score", 0),
                    "engagement_score": scores.get("engagement_score", 0),
                    "youtube_views": video_data.get("youtube_views", 0),
                    "is_new_release": video_data.get("is_new_release", False)
                })
            
            # Sort by score (descending)
            videos.sort(key=lambda x: x["score"], reverse=True)
            
            # Ensure new releases get exposure
            if include_new_releases:
                # Find any new releases not already in the top videos
                new_releases = [v for v in self.scores_data["videos"].values() 
                               if v.get("is_new_release", False)]
                
                # Ensure at least 20% of results are new releases if available
                min_new_releases = max(1, limit // 5)
                top_video_ids = [v["id"] for v in videos[:limit]]
                new_release_count = sum(1 for v in videos[:limit] 
                                      if v.get("is_new_release", False))
                
                if new_release_count < min_new_releases and new_releases:
                    # Add new releases not already in the top videos
                    additional_new_releases = []
                    for video in new_releases:
                        video_id = video.get("id")
                        if video_id and video_id not in top_video_ids:
                            scores = video.get("scores", {})
                            additional_new_releases.append({
                                "id": video_id,
                                "title": video.get("title", "Unknown"),
                                "score": scores.get("total_score", 0),
                                "base_score": scores.get("base_score", 0),
                                "engagement_score": scores.get("engagement_score", 0),
                                "youtube_views": video.get("youtube_views", 0),
                                "is_new_release": True
                            })
                    
                    # Sort new releases by score
                    additional_new_releases.sort(key=lambda x: x["score"], reverse=True)
                    
                    # Add enough new releases to meet the minimum
                    needed = min_new_releases - new_release_count
                    if needed > 0 and additional_new_releases:
                        # Replace lowest scoring non-new videos with new releases
                        non_new_indices = [i for i, v in enumerate(videos[:limit]) 
                                         if not v.get("is_new_release", False)]
                        
                        # Start from the end to replace lowest scores
                        for i in range(min(needed, len(additional_new_releases))):
                            if i < len(non_new_indices):
                                replace_idx = non_new_indices[-(i+1)]
                                if replace_idx < limit:
                                    videos[replace_idx] = additional_new_releases[i]
                        
                        # Re-sort after replacements
                        videos.sort(key=lambda x: x["score"], reverse=True)
            
            # Filter by playlist if specified
            if playlist_id:
                playlist_videos = self._get_playlist_videos(playlist_id)
                videos = [v for v in videos if v["id"] in playlist_videos]
            
            # Return the top videos up to the limit
            return videos[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top videos: {str(e)}")
            return []
    
    def _get_playlist_videos(self, playlist_id: str) -> List[str]:
        """Get video IDs for a specific playlist."""
        # This function would need to access your download_history to find videos in a playlist
        # For this example, we'll just return an empty list
        # In a real implementation, you would connect this to your download history data
        return []
    
    def get_current_time_slot(self) -> str:
        """
        Determine the current time slot based on UTC time.
        
        Returns:
            Current time slot label
        """
        # Get current UTC hour
        current_hour = datetime.utcnow().hour
        
        # Check each time slot
        if 22 <= current_hour or current_hour < 3:
            return "US_PrimeTime"
        elif 18 <= current_hour < 22:
            return "UK_Evening"
        elif 10 <= current_hour < 16:
            return "PH_Evening"
        else:
            return "Low_Traffic"
    
    def update_playlist_performance(self, playlist_id: str, name: str, 
                                  viewer_change: int) -> bool:
        """
        Update performance metrics for a playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            name: Playlist name
            viewer_change: Average viewer change during playback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "playlists" not in self.scores_data:
                self.scores_data["playlists"] = {}
                
            if playlist_id not in self.scores_data["playlists"]:
                # Create new playlist entry
                self.scores_data["playlists"][playlist_id] = {
                    "name": name,
                    "performance_factor": 1.0,
                    "avg_viewer_change": viewer_change,
                    "data_points": 1
                }
            else:
                # Update existing playlist
                playlist = self.scores_data["playlists"][playlist_id]
                data_points = playlist.get("data_points", 1)
                prev_avg = playlist.get("avg_viewer_change", 0)
                
                # Calculate new average
                new_avg = ((prev_avg * data_points) + viewer_change) / (data_points + 1)
                
                playlist["name"] = name
                playlist["avg_viewer_change"] = new_avg
                playlist["data_points"] = data_points + 1
                
                # Update performance factor based on average viewer change
                # Scale from 0.5 to 1.5 based on performance
                if new_avg > 0:
                    # Positive change: Scale 0-200 to 1.0-1.5
                    performance_factor = 1.0 + min(0.5, new_avg / 400)
                else:
                    # Negative change: Scale 0 to -100 to 1.0-0.5
                    performance_factor = 1.0 + max(-0.5, new_avg / 200)
                
                playlist["performance_factor"] = performance_factor
            
            return self._save_scores()
            
        except Exception as e:
            logger.error(f"Error updating playlist performance: {str(e)}")
            return False