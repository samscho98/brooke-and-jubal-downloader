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
        
    def _ensure_output_dir_exists(self):
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def download_video(self, video_url: str, audio_only: bool = True, playlist_name: Optional[str] = None) -> Optional[str]:
        """
        Download a single video from YouTube.
        
        Args:
            video_url: URL of the YouTube video
            audio_only: If True, download only the audio
            playlist_name: Optional name of the playlist for organizing downloads
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        try:
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
            }
            
            if audio_only:
                options['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': str(bitrate_value),
                }]
            
            with yt_dlp.YoutubeDL(options) as ydl:
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
                        normalized_file = AudioConverter.normalize_audio(
                            downloaded_file, 
                            target_level=target_level
                        )
                        if normalized_file:
                            logger.info(f"Audio normalized to target level: {target_level} dB")
                            downloaded_file = normalized_file
                    except Exception as e:
                        logger.error(f"Error normalizing audio: {str(e)}")
                
                logger.info(f"Successfully downloaded: {info.get('title')}")
                return downloaded_file
                
        except Exception as e:
            logger.error(f"Error downloading video {video_url}: {str(e)}")
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
            'extract_flat': True,
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
                
                # Extract relevant info for each video
                videos = []
                for entry in playlist_info['entries']:
                    if entry:
                        video_info = {
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'duration': entry.get('duration'),
                            'uploader': entry.get('uploader'),
                        }
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
                successful.append({
                    'id': video['id'],
                    'title': video['title'],
                    'file_path': result
                })
            else:
                failed.append(video['id'])
                
        return successful, failed