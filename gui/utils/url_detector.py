"""
URL detection utility to identify YouTube URLs.
"""
import re
import logging

def identify_youtube_url(url: str) -> tuple:
    """
    Identify the type of YouTube URL and extract relevant information.
    
    Args:
        url: The URL to identify
        
    Returns:
        tuple: (url_type, id, start_time)
            url_type can be "video", "playlist", "channel", or "unknown"
            id is the video ID, playlist ID, or channel ID
            start_time is the start time in seconds (if present in the URL)
    """
    if not url:
        return "unknown", None, None
        
    url = url.strip()
    
    # Video URL patterns
    video_patterns = [
        # Standard watch URLs
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(?:&.*)?$',
        # Short youtu.be URLs
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})(?:\?.*)?$'
    ]
    
    # Playlist URL patterns
    playlist_patterns = [
        # Standard playlist URLs
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)(?:&.*)?$',
        # Watch URL with playlist parameter
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*list=([a-zA-Z0-9_-]+)(?:&.*)?$'
    ]
    
    # Channel URL patterns
    channel_patterns = [
        # Channel URLs
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/([a-zA-Z0-9_-]+)(?:\/.*)?$',
        # User URLs
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/user\/([a-zA-Z0-9_-]+)(?:\/.*)?$'
    ]
    
    # Check for video URLs
    for pattern in video_patterns:
        match = re.match(pattern, url)
        if match:
            video_id = match.group(1)
            
            # Check for start time parameter
            start_time = None
            start_time_match = re.search(r'[?&]t=(\d+|(?:\d+m\d+s))(?:&|$)', url)
            if start_time_match:
                time_str = start_time_match.group(1)
                if 'm' in time_str and 's' in time_str:
                    # Format: 1m30s
                    minutes, seconds = time_str.split('m')
                    seconds = seconds.rstrip('s')
                    start_time = int(minutes) * 60 + int(seconds)
                else:
                    # Format: seconds
                    start_time = int(time_str)
            
            return "video", video_id, start_time
    
    # Check for playlist URLs
    for pattern in playlist_patterns:
        match = re.match(pattern, url)
        if match:
            playlist_id = match.group(1)
            return "playlist", playlist_id, None
    
    # Check for channel URLs
    for pattern in channel_patterns:
        match = re.match(pattern, url)
        if match:
            channel_id = match.group(1)
            return "channel", channel_id, None
    
    return "unknown", None, None