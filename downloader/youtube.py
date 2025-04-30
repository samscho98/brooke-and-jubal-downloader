"""
YouTube video downloader module.
Responsible for downloading videos from YouTube playlists.
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
import yt_dlp

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Class to handle YouTube video downloading operations."""
    
    def __init__(self, output_dir: str = "data/audio"):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded files
        """
        self.output_dir = output_dir
        self._ensure_output_dir_exists()
        
    def _ensure_output_dir_exists(self):
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def download_video(self, video_url: str, audio_only: bool = True) -> Optional[str]:
        """
        Download a single video from YouTube.
        
        Args:
            video_url: URL of the YouTube video
            audio_only: If True, download only the audio
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        try:
            options = {
                'format': 'bestaudio/best' if audio_only else 'best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
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
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(video_url, download=True)
                if audio_only:
                    # The file will be named with .mp3 extension
                    downloaded_file = os.path.join(
                        self.output_dir, 
                        ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
                    )
                else:
                    downloaded_file = os.path.join(
                        self.output_dir, 
                        ydl.prepare_filename(info)
                    )
                
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
            
    def download_playlist(self, playlist_url: str, audio_only: bool = True) -> Tuple[List[str], List[str]]:
        """
        Download all videos from a YouTube playlist.
        
        Args:
            playlist_url: URL of the YouTube playlist
            audio_only: If True, download only the audio
            
        Returns:
            Tuple of (list of successful downloads, list of failed video IDs)
        """
        videos = self.get_playlist_videos(playlist_url)
        
        successful = []
        failed = []
        
        for video in videos:
            video_url = video['url']
            result = self.download_video(video_url, audio_only)
            
            if result:
                successful.append({
                    'id': video['id'],
                    'title': video['title'],
                    'file_path': result
                })
            else:
                failed.append(video['id'])
                
        return successful, failed