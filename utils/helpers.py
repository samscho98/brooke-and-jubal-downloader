"""
Helper functions for the YouTube Playlist Downloader.
"""
import os
import re
import logging
from typing import Optional

def clean_filename(filename: str) -> str:
    """
    Clean a filename to make it filesystem-safe.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    if not filename:
        return "unnamed"
    
    # Remove illegal characters
    clean = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace multiple spaces with a single space
    clean = re.sub(r'\s+', " ", clean)
    # Trim whitespace
    clean = clean.strip()
    
    # If filename is empty after cleaning, use a default name
    if not clean:
        return "unnamed"
        
    # Limit length
    if len(clean) > 200:
        clean = clean[:197] + "..."
        
    return clean

def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Human-readable duration string (MM:SS or HH:MM:SS)
    """
    if seconds is None or seconds < 0:
        return "0:00"
        
    # Convert to integers
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def format_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes is None or size_bytes < 0:
        return "0 B"
        
    # Define units
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    # Determine unit index
    unit_index = 0
    size = float(size_bytes)
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
        
    # Format the size
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"

def ensure_directory(directory: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
        
    Returns:
        True if the directory exists or was created, False on error
    """
    if not directory:
        return False
        
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {str(e)}")
        return False

def get_file_extension(file_path: str) -> Optional[str]:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (without the dot) or None if no extension
    """
    if not file_path:
        return None
        
    _, ext = os.path.splitext(file_path)
    
    if not ext:
        return None
        
    # Remove the dot
    ext = ext[1:] if ext.startswith('.') else ext
    
    return ext.lower()

def is_audio_file(file_path: str) -> bool:
    """
    Check if a file is an audio file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is an audio file, False otherwise
    """
    if not file_path:
        return False
        
    # List of common audio file extensions
    audio_extensions = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma']
    
    ext = get_file_extension(file_path)
    
    return ext in audio_extensions

def is_video_file(file_path: str) -> bool:
    """
    Check if a file is a video file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a video file, False otherwise
    """
    if not file_path:
        return False
        
    # List of common video file extensions
    video_extensions = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']
    
    ext = get_file_extension(file_path)
    
    return ext in video_extensions

def parse_youtube_url(url: str) -> tuple:
    """
    Parse a YouTube URL to extract ID and type.
    
    Args:
        url: YouTube URL
        
    Returns:
        Tuple of (type, id) where type is 'video', 'playlist', or None
    """
    if not url:
        return None, None
        
    # Clean the URL
    url = url.strip()
    
    # Match video ID
    video_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    if video_match:
        return 'video', video_match.group(1)
        
    # Match playlist ID
    playlist_match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if playlist_match:
        return 'playlist', playlist_match.group(1)
        
    return None, None