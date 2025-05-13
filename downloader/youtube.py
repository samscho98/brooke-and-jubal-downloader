"""
YouTube video downloader module.
Responsible for downloading videos from YouTube playlists.
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
import yt_dlp
from data.config_manager import ConfigHandler
from utils.path_utils import clean_output_path

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Class to handle YouTube video downloading operations."""
    
    def __init__(self, output_dir: str = "data/audio", config: Optional[ConfigHandler] = None, tracker = None):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded files
            config: Optional configuration handler
            tracker: Optional download tracker for updating history
        """
        self.output_dir = output_dir
        self._ensure_output_dir_exists()
        
        # Initialize with default config or use provided config
        if config is None:
            self.config = ConfigHandler()
        else:
            self.config = config
        
        # Store the tracker reference
        self.tracker = tracker
        
        # Explicitly set FFmpeg path for yt-dlp
        from downloader.converter import FFMPEG_PATH
        if FFMPEG_PATH:
            self.ffmpeg_location = FFMPEG_PATH
        else:
            self.ffmpeg_location = None
        
    def _ensure_output_dir_exists(self):
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        Get detailed information about a YouTube video including view count and comments.
        
        Args:
            video_url: URL of the YouTube video
            
        Returns:
            Dictionary containing video information or None if retrieval failed
        """
        options = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,  # We want full info
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if info:
                    # Extract just the information we need
                    video_info = {
                        'id': info.get('id'),
                        'title': info.get('title'),
                        'view_count': info.get('view_count', 0),
                        'comment_count': info.get('comment_count', 0),  # Make sure to get comment count
                        'like_count': info.get('like_count', 0),
                        'dislike_count': info.get('dislike_count', 0),
                        'uploader': info.get('uploader'),
                        'upload_date': info.get('upload_date'),
                        'duration': info.get('duration', 0),
                        'categories': info.get('categories', []),
                        'tags': info.get('tags', []),
                        'url': video_url
                    }
                    
                    logger.info(f"Retrieved info for video: {video_info['title']} (Views: {video_info['view_count']}, Comments: {video_info['comment_count']})")
                    return video_info
                    
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving video info for {video_url}: {str(e)}")
            return None
    
    def download_video(self, video_url: str, audio_only: bool = True, playlist_name: Optional[str] = None) -> Optional[Tuple[str, Dict]]:
        """
        Download a single video from YouTube.
        
        Args:
            video_url: URL of the YouTube video
            audio_only: If True, download only the audio
            playlist_name: Optional name of the playlist for organizing downloads
            
        Returns:
            Tuple of (path to the downloaded file, video info dict) or None if download failed
        """
        try:
            # First get video info including view count
            video_info = self.get_video_info(video_url)
            if not video_info:
                logger.error(f"Could not retrieve video info for {video_url}")
                return None
                
            # Get audio format and bitrate from config
            audio_format = self.config.get("audio", "format", "mp3")
            audio_bitrate = self.config.get("audio", "bitrate", "192k")
            
            # Extract bitrate as integer value for yt-dlp
            bitrate_value = audio_bitrate.rstrip('k')
            try:
                bitrate_value = int(bitrate_value)
            except ValueError:
                bitrate_value = 192  # Default if parsing fails
            
            # Create playlist subfolder if provided
            output_dir = self.output_dir
            if playlist_name:
                # Clean the playlist name to make it a valid folder name
                import re
                clean_name = re.sub(r'[\\/*?:"<>|]', '_', playlist_name).strip()
                playlist_dir = os.path.join(self.output_dir, clean_name)
                if not os.path.exists(playlist_dir):
                    os.makedirs(playlist_dir, exist_ok=True)
                    logger.info(f"Created playlist directory: {playlist_dir}")
                output_dir = playlist_dir
            
            options = {
                'format': 'bestaudio/best' if audio_only else 'best',
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'default_search': 'auto',
                'source_address': '0.0.0.0',
                # Extract additional metadata for scoring
                'writeinfojson': False,  # Don't write info.json file
                'writethumbnail': False,  # Don't download thumbnail
            }
            
            # Add FFmpeg location if available
            if hasattr(self, 'ffmpeg_location') and self.ffmpeg_location:
                options['ffmpeg_location'] = self.ffmpeg_location
            
            if audio_only:
                options['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': str(bitrate_value),
                }]
            
            with yt_dlp.YoutubeDL(options) as ydl:
                logger.info(f"Downloading video: {video_url}")
                info = ydl.extract_info(video_url, download=True)
                if audio_only:
                    # The file will be named with the specified audio format extension
                    downloaded_file = os.path.join(
                        output_dir, 
                        ydl.prepare_filename(info).rsplit(".", 1)[0] + f".{audio_format}"
                    )
                else:
                    downloaded_file = os.path.join(
                        output_dir, 
                        ydl.prepare_filename(info)
                    )
                
                # Apply audio normalization if enabled
                normalize_audio = self.config.getboolean("audio", "normalize_audio", False)
                if normalize_audio and audio_only and os.path.exists(downloaded_file):
                    try:
                        from downloader.converter import AudioConverter
                        target_level = self.config.getfloat("audio", "target_level", -18.0)
                        logger.info(f"Normalizing audio to target level: {target_level} dB")
                        normalized_file = AudioConverter.normalize_audio(
                            downloaded_file, 
                            target_level=target_level
                        )
                        if normalized_file:
                            logger.info(f"Audio normalized to target level: {target_level} dB")
                            downloaded_file = normalized_file
                    except Exception as e:
                        logger.error(f"Error normalizing audio: {str(e)}")
                
                # Extract additional metadata for scoring system
                video_data = {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown Title'),
                    'view_count': info.get('view_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'like_count': info.get('like_count', 0),
                    'dislike_count': info.get('dislike_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'uploader': info.get('uploader', ''),
                    'duration': info.get('duration', 0),
                    'categories': info.get('categories', []),
                    'tags': info.get('tags', []),
                    'url': video_url
                }
                
                # Update the scoring system with video metadata
                try:
                    from downloader.scoring import ScoringSystem
                    from utils.path_utils import get_data_path
                    
                    # Use path_utils to get the correct path
                    scoring = ScoringSystem(get_data_path("video_scores.json"))
                    
                    # Determine if this is a new release (less than 14 days old)
                    is_new_release = False
                    if video_data.get('upload_date'):
                        from datetime import datetime
                        try:
                            upload_date = datetime.strptime(video_data['upload_date'], '%Y%m%d')
                            days_since_upload = (datetime.now() - upload_date).days
                            is_new_release = days_since_upload < 14
                        except ValueError:
                            # If date parsing fails, default to False
                            pass
                    
                    # Update scoring system with this video's data
                    scoring.update_video_metadata(
                        video_id=video_data['id'],
                        title=video_data['title'],
                        youtube_views=video_data['view_count'],
                        youtube_comments=video_data['comment_count'],
                        upload_date=video_data['upload_date'],
                        is_new_release=is_new_release
                    )
                    
                    # Extract playlist ID if available
                    playlist_id = None
                    if playlist_name and "list=" in video_url:
                        import re
                        playlist_match = re.search(r'list=([^&]+)', video_url)
                        if playlist_match:
                            playlist_id = playlist_match.group(1)
                            
                            # Update playlist in scoring system if we have a playlist ID
                            if playlist_id:
                                logger.info(f"Updating playlist in scoring system: {playlist_id}")
                                # Default values for initial playlist addition
                                scoring.update_playlist_performance(
                                    playlist_id=playlist_id,
                                    name=playlist_name,
                                    viewer_change=0  # Default neutral value for initial addition
                                )
                    
                    logger.info(f"Updated scoring system for video: {video_data['title']}")
                    
                except Exception as e:
                    logger.warning(f"Error updating scoring system: {str(e)}")
                    import traceback
                    logger.debug(traceback.format_exc())
                
                # Update download tracker if available
                if hasattr(self, 'tracker') and self.tracker is not None:
                    try:
                        # Extract video ID
                        video_id = video_data['id']
                        
                        # Default playlist ID for single videos
                        playlist_id = "other_videos"
                        
                        # Extract playlist ID if available
                        if "list=" in video_url:
                            import re
                            playlist_match = re.search(r'list=([^&]+)', video_url)
                            if playlist_match:
                                playlist_id = playlist_match.group(1)
                        
                        # This prevents the duplication of paths
                        from utils.path_utils import get_path
                        
                        # Get the absolute app root path
                        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        
                        # Convert absolute path to relative path from app root
                        if downloaded_file.startswith(app_root):
                            relative_path = os.path.relpath(downloaded_file, app_root)
                            logger.info(f"Converting path from '{downloaded_file}' to '{relative_path}'")
                            file_path_to_store = relative_path
                        else:
                            # If not under app root, keep the original path
                            file_path_to_store = downloaded_file

                        # Add to download history
                        logger.info(f"Adding to download history: {video_data['title']}")
                        # Before adding to download history, clean the path
                        file_path_to_store = clean_output_path(downloaded_file)

                        self.tracker.add_downloaded_video(
                            video_id=video_id,
                            playlist_id=playlist_id,
                            title=video_data['title'],
                            file_path=file_path_to_store,
                            view_count=video_data['view_count'],
                            comment_count=video_data['comment_count'],
                            upload_date=video_data['upload_date'],
                            duration_seconds=video_data['duration']
                        )
                        logger.info(f"Successfully added to download history: {video_data['title']}")
                    except Exception as e:
                        logger.error(f"Error updating download history: {str(e)}")
                        import traceback
                        logger.debug(traceback.format_exc())
                else:
                    logger.warning("No tracker available to update download history")
                
                logger.info(f"Successfully downloaded: {info.get('title')} (Views: {video_data['view_count']})")
                return downloaded_file, video_data
                
        except Exception as e:
            logger.error(f"Error downloading video {video_url}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def get_playlist_videos(self, playlist_url: str) -> List[Dict]:
        """
        Get information about all videos in a playlist without downloading them.
        
        Args:
            playlist_url: URL of the YouTube playlist
            
        Returns:
            List of dictionaries containing video information
        """
        options = {
            'extract_flat': True,  # First use extract_flat to get video IDs quickly
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if 'entries' not in playlist_info:
                    logger.error(f"No videos found in playlist: {playlist_url}")
                    return []
                
                # Extract basic info for each video and then get detailed info
                videos = []
                for entry in playlist_info['entries']:
                    if entry:
                        video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                        
                        # Get basic info from the flat extraction
                        video_info = {
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': video_url,
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader'),
                            'view_count': 0,  # Default value, will try to update
                            'comment_count': 0,  # Default value for comments
                            'upload_date': None  # Default value for upload date
                        }
                        
                        # Attempt to get detailed info including view count, comment count, and upload date
                        try:
                            detailed_info = self.get_video_info(video_url)
                            if detailed_info:
                                # Update with detailed info if available
                                video_info['view_count'] = detailed_info.get('view_count', 0)
                                video_info['comment_count'] = detailed_info.get('comment_count', 0)
                                video_info['upload_date'] = detailed_info.get('upload_date')
                                
                                # If duration wasn't in flat info, get it from detailed info
                                if not video_info['duration'] and 'duration' in detailed_info:
                                    video_info['duration'] = detailed_info['duration']
                                    
                                # Copy any additional metadata that might be useful
                                for key in ['like_count', 'dislike_count', 'categories', 'tags']:
                                    if key in detailed_info:
                                        video_info[key] = detailed_info[key]
                        except Exception as e:
                            logger.warning(f"Could not get detailed info for {video_url}: {str(e)}")
                        
                        videos.append(video_info)
                
                logger.info(f"Found {len(videos)} videos in playlist: {playlist_url}")
                return videos
                
        except Exception as e:
            logger.error(f"Error retrieving playlist {playlist_url}: {str(e)}")
            return []
            
    def download_playlist(self, playlist_url: str, audio_only: bool = True, playlist_name: Optional[str] = None) -> Tuple[List[Dict], List[str]]:
        """
        Download all videos from a YouTube playlist.
        
        Args:
            playlist_url: URL of the YouTube playlist
            audio_only: If True, download only the audio
            playlist_name: Optional name of the playlist for organizing downloads
            
        Returns:
            Tuple of (list of successful downloads, list of failed video IDs)
        """
        videos = self.get_playlist_videos(playlist_url)
        
        successful = []
        failed = []
        
        # Get max downloads from config
        max_downloads = self.config.getint("general", "max_downloads", 10)
        
        # Limit to max_downloads if set
        if max_downloads > 0 and len(videos) > max_downloads:
            logger.info(f"Limiting downloads to {max_downloads} videos (out of {len(videos)})")
            videos = videos[:max_downloads]
        
        for video in videos:
            video_url = video['url']
            result = self.download_video(video_url, audio_only, playlist_name)
            
            if result:
                downloaded_file, video_info = result
        
                # If we have a tracker, update it
                if self.tracker:
                    # Extract video ID from URL
                    import re
                    if "youtube.com/watch" in video_url:
                        match = re.search(r'v=([^&]+)', video_url)
                        if match:
                            video_id = match.group(1)
                    elif "youtu.be/" in video_url:
                        match = re.search(r'youtu\.be/([^?]+)', video_url)
                        if match:
                            video_id = match.group(1)
                    else:
                        video_id = video_info.get('id', '')
                        
                    # Extract playlist ID from URL
                    playlist_id = "other_videos"  # Default for single videos
                    if "list=" in video_url:
                        playlist_match = re.search(r'list=([^&]+)', video_url)
                        if playlist_match:
                            playlist_id = playlist_match.group(1)
                            
                    # Add to download history
                    self.tracker.add_downloaded_video(
                        video_id=video_id,
                        playlist_id=playlist_id,
                        title=video_info.get('title', 'Unknown Title'),
                        file_path=downloaded_file,
                        view_count=video_info.get('view_count', 0),
                        comment_count=video_info.get('comment_count', 0),
                        upload_date=video_info.get('upload_date'),
                        duration_seconds=video_info.get('duration', 0)
                    )
            else:
                failed.append(video['id'])
                
        return successful, failed