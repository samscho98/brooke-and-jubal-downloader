"""
YouTube video downloader module.
Responsible for downloading videos from YouTube playlists.
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
import yt_dlp
from utils.config_handler import ConfigHandler

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Class to handle YouTube video downloading operations."""
    
    def __init__(self, output_dir: str = "data/audio", config: Optional[ConfigHandler] = None):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded files
            config: Optional configuration handler
        """
        self.output_dir = output_dir
        self._ensure_output_dir_exists()
        
        # Initialize with default config or use provided config
        if config is None:
            self.config = ConfigHandler()
        else:
            self.config = config
        
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
        Get detailed information about a YouTube video including view count.
        
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
                        'uploader': info.get('uploader'),
                        'upload_date': info.get('upload_date'),
                        'duration': info.get('duration'),
                        'url': video_url
                    }
                    
                    logger.info(f"Retrieved info for video: {video_info['title']} (Views: {video_info['view_count']})")
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
                    scoring = ScoringSystem()
                    
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
                            'duration': entry.get('duration'),
                            'uploader': entry.get('uploader'),
                            'view_count': 0  # Default value, will try to update
                        }
                        
                        # Attempt to get detailed info for view count
                        # If it fails, we still have the basic info
                        try:
                            detailed_info = self.get_video_info(video_url)
                            if detailed_info and 'view_count' in detailed_info:
                                video_info['view_count'] = detailed_info['view_count']
                                video_info['upload_date'] = detailed_info.get('upload_date')
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
                successful.append({
                    'id': video['id'],
                    'title': video['title'],
                    'file_path': downloaded_file,
                    'view_count': video_info.get('view_count', 0),
                    'upload_date': video_info.get('upload_date')
                })
            else:
                failed.append(video['id'])
                
        return successful, failed