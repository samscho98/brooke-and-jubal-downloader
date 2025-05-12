#!/usr/bin/env python3
"""
CLI commands module.
Implements command-line interface commands.
"""
import os
import re
import logging
from typing import Optional, List, Dict, Tuple

def download_command(downloader, tracker, url: str) -> int:
    """
    Download a YouTube video or playlist.
    
    Args:
        downloader: YouTubeDownloader instance
        tracker: DownloadTracker instance
        url: YouTube URL to download
        
    Returns:
        Exit code
    """
    if not url:
        print("Error: URL is required")
        return 1
    
    print(f"Downloading: {url}")
    
    if "list=" in url:  # It's a playlist
        print("Detected playlist URL")
        # Try to get playlist name 
        playlist_name = None
        for playlist in tracker.get_playlists():
            if playlist["url"] == url:
                playlist_name = playlist["name"]
                break
                
        if not playlist_name:
            playlist_name = input("Enter a name for this playlist (for folder organization): ")
            
        successful, failed = downloader.download_playlist(url, audio_only=True, playlist_name=playlist_name)
        
        print(f"\nDownloaded {len(successful)} videos, {len(failed)} failed")
        if failed:
            print("Failed videos:")
            for video_id in failed:
                print(f"  - {video_id}")
    else:  # It's a single video
        print("Detected single video URL")
        # Use "Other" as the default playlist name for individual videos
        result = downloader.download_video(url, audio_only=True, playlist_name="Other")
        
        if result:
            downloaded_file, video_info = result
            print(f"Successfully downloaded to: {downloaded_file}")
            print(f"Views: {video_info.get('view_count', 0):,}")
            
            # Extract video ID from URL
            video_id = None
            if "youtube.com/watch" in url:
                match = re.search(r'v=([^&]+)', url)
                if match:
                    video_id = match.group(1)
            elif "youtu.be/" in url:
                match = re.search(r'youtu\.be/([^?]+)', url)
                if match:
                    video_id = match.group(1)
            
            # Add to download history if we could get the ID
            if video_id:
                # Special playlist ID for single videos
                playlist_id = "other_videos"
                
                # Extract additional metadata required for scoring
                comment_count = video_info.get('comment_count', 0)
                duration_seconds = video_info.get('duration', 0)
                
                # Add all information to the tracker
                tracker.add_downloaded_video(
                    video_id=video_id,
                    playlist_id=playlist_id,
                    title=video_info.get('title', 'Unknown Title'),
                    file_path=downloaded_file,
                    view_count=video_info.get('view_count', 0),
                    comment_count=comment_count,
                    upload_date=video_info.get('upload_date'),
                    duration_seconds=duration_seconds
                )
        else:
            print("Failed to download video")
            return 1
    
    return 0

def add_playlist_command(tracker, url: str) -> int:
    """
    Add a playlist to track.
    
    Args:
        tracker: DownloadTracker instance
        url: YouTube playlist URL
        
    Returns:
        Exit code
    """
    if not url:
        print("Error: URL is required")
        return 1
    
    name = input("Enter a name for this playlist: ")
    interval = input("Check interval in hours (default: 24): ")
    
    if not interval.strip():
        interval = "24"
        
    try:
        interval = int(interval)
        success = tracker.add_playlist(
            url=url,
            name=name,
            check_interval=interval
        )
        
        if success:
            print(f"Successfully added playlist: {name}")
            return 0
        else:
            print("Failed to add playlist")
            return 1
            
    except ValueError:
        print("Invalid check interval. Using default: 24 hours")
        success = tracker.add_playlist(
            url=url,
            name=name
        )
        if success:
            print(f"Successfully added playlist: {name}")
            return 0
        else:
            print("Failed to add playlist")
            return 1

def list_playlists_command(tracker) -> int:
    """
    List all tracked playlists.
    
    Args:
        tracker: DownloadTracker instance
        
    Returns:
        Exit code
    """
    playlists = tracker.get_playlists()
    
    if not playlists:
        print("No playlists are currently being tracked")
        return 0
    
    print(f"\nTracked Playlists ({len(playlists)}):")
    print("-" * 80)
    for i, playlist in enumerate(playlists, 1):
        name = playlist.get("name", "Unnamed Playlist")
        url = playlist.get("url", "N/A")
        interval = playlist.get("check_interval", 24)
        last_checked = playlist.get("last_checked", "Never")
        
        # Format last_checked if it's a datetime
        if last_checked is not None and last_checked != "Never":
            from datetime import datetime
            try:
                last_checked = datetime.fromisoformat(last_checked).strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid date format for playlist {name}: {e}")
                last_checked = str(last_checked)
        
        print(f"{i}. {name}")
        print(f"   URL: {url}")
        print(f"   Check Interval: {interval} hours")
        print(f"   Last Checked: {last_checked}")
        print()
    
    return 0

def update_playlists_command(tracker, downloader, config) -> int:
    """
    Update all playlists that need updating based on their check interval.
    
    Args:
        tracker: DownloadTracker instance
        downloader: YouTubeDownloader instance
        config: ConfigHandler instance
        
    Returns:
        Exit code
    """
    playlists_to_update = tracker.check_for_updates()
    
    if not playlists_to_update:
        print("No playlists need updating at this time")
        return 0
    
    print(f"Updating {len(playlists_to_update)} playlists...")
    
    # Get audio settings from config
    audio_format = config.get("audio", "format", "mp3")
    audio_bitrate = config.get("audio", "bitrate", "192k")
    normalize_audio = config.getboolean("audio", "normalize_audio", False)
    target_level = config.getfloat("audio", "target_level", -18.0)
    
    for playlist in playlists_to_update:
        url = playlist.get("url")
        name = playlist.get("name", "Unnamed Playlist")
        
        print(f"\nProcessing playlist: {name}")
        print(f"URL: {url}")
        
        # Get videos in the playlist
        videos = downloader.get_playlist_videos(url)
        
        if not videos:
            print("No videos found in playlist or error retrieving playlist")
            continue
        
        print(f"Found {len(videos)} videos in playlist")
        
        # Check which videos have already been downloaded
        new_videos = [v for v in videos if not tracker.is_video_downloaded(v['id'])]
        
        if not new_videos:
            print("All videos have already been downloaded")
            # Update the last checked time even if no new videos
            tracker.update_playlist_check_time(url)
            continue
        else:
            print(f"Found {len(new_videos)} new videos to download...")
            
            for i, video in enumerate(new_videos, 1):
                print(f"  [{i}/{len(new_videos)}] Downloading: {video['title']}")
                
                # Extract playlist ID from URL
                import re
                playlist_id_match = re.search(r'list=([^&]+)', url)
                playlist_id = playlist_id_match.group(1) if playlist_id_match else "unknown"
                
                # Download the video
                result = downloader.download_video(video['url'], audio_only=True, playlist_name=name)
                
                if result:
                    downloaded_file, video_info = result
                    
                    # Check if we need to convert the file format
                    file_ext = os.path.splitext(downloaded_file)[1].lower().lstrip('.')
                    if file_ext != audio_format:
                        from downloader.converter import AudioConverter
                        print(f"    Converting to {audio_format} format...")
                        converted_file = AudioConverter.convert_audio(
                            downloaded_file, 
                            audio_format, 
                            bitrate=audio_bitrate
                        )
                        if converted_file:
                            # Remove the original file if conversion was successful
                            if os.path.exists(downloaded_file) and downloaded_file != converted_file:
                                os.remove(downloaded_file)
                            downloaded_file = converted_file
                    
                    # Add to download history with view count
                    tracker.add_downloaded_video(
                        video_id=video['id'],
                        playlist_id=playlist_id,
                        title=video['title'],
                        file_path=downloaded_file,
                        view_count=video_info.get('view_count', 0),
                        upload_date=video_info.get('upload_date')
                    )
                    print(f"    ✓ Downloaded to: {downloaded_file}")
                    print(f"    ✓ Views: {video_info.get('view_count', 0):,}")
                else:
                    print(f"    ✗ Failed to download")
        
        # Update the last checked time
        tracker.update_playlist_check_time(url)
    
    return 0

def remove_playlist_command(tracker, url: str) -> int:
    """
    Remove a playlist from tracking.
    
    Args:
        tracker: DownloadTracker instance
        url: YouTube playlist URL
        
    Returns:
        Exit code
    """
    if not url:
        print("Error: URL is required")
        return 1
    
    success = tracker.remove_playlist(url)
    if success:
        print(f"Successfully removed playlist: {url}")
        return 0
    else:
        print(f"Failed to remove playlist: {url}")
        return 1

def update_view_counts_command(tracker, downloader) -> int:
    """
    Update view counts for all downloaded videos.
    
    Args:
        tracker: DownloadTracker instance
        downloader: YouTubeDownloader instance
        
    Returns:
        Exit code
    """
    print("\nUpdating view counts for all downloaded videos...")
    print("This may take a while depending on the number of videos.")
    print("Please be patient and avoid interrupting the process.\n")
    
    # Get the total number of videos
    videos = tracker.get_downloaded_videos()
    total_videos = len(videos)
    
    if total_videos == 0:
        print("No videos in the download history")
        return 0
    
    print(f"Found {total_videos} videos to update")
    
    # Perform the update
    updated, failed = tracker.bulk_update_view_counts(downloader)
    
    print("\nView Count Update Complete")
    print(f"Successfully updated: {updated} videos")
    print(f"Failed to update: {failed} videos")
    
    if updated > 0:
        # Show the top 5 videos by view count after update
        display_top_videos_command(tracker, 5)
    
    return 0

def display_video_stats_command(tracker) -> int:
    """
    Display statistics about downloaded videos.
    
    Args:
        tracker: DownloadTracker instance
        
    Returns:
        Exit code
    """
    stats = tracker.get_video_stats()
    
    print("\nVideo Collection Statistics:")
    print("-" * 80)
    print(f"Total Videos: {stats['total_videos']}")
    print(f"Total Views: {stats['total_views']:,}")
    print(f"Average Views per Video: {stats['avg_views']:,.2f}")
    
    if stats['max_views_video']:
        print(f"\nMost Viewed Video: {stats['max_views_video']['title']}")
        print(f"   ID: {stats['max_views_video']['id']}")
        print(f"   Views: {stats['max_views_video']['view_count']:,}")
    
    if stats['newest_video']:
        from datetime import datetime
        date_str = stats['newest_video']['date']
        try:
            # Format YYYYMMDD to more readable format
            formatted_date = datetime.strptime(date_str, "%Y%m%d").strftime("%B %d, %Y")
        except:
            formatted_date = date_str
            
        print(f"\nNewest Video: {stats['newest_video']['title']}")
        print(f"   Uploaded: {formatted_date}")
    
    if stats['oldest_video']:
        from datetime import datetime
        date_str = stats['oldest_video']['date']
        try:
            # Format YYYYMMDD to more readable format
            formatted_date = datetime.strptime(date_str, "%Y%m%d").strftime("%B %d, %Y")
        except:
            formatted_date = date_str
            
        print(f"\nOldest Video: {stats['oldest_video']['title']}")
        print(f"   Uploaded: {formatted_date}")
    
    return 0

def display_top_videos_command(tracker, limit: int = 10) -> int:
    """
    Display top videos by view count.
    
    Args:
        tracker: DownloadTracker instance
        limit: Number of videos to display
        
    Returns:
        Exit code
    """
    videos = tracker.get_downloaded_videos()
    
    if not videos:
        print("No videos in the download history")
        return 0
    
    # Sort videos by view count (descending)
    videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)
    
    print(f"\nTop {min(limit, len(videos))} Videos by View Count:")
    print("-" * 80)
    
    for i, video in enumerate(videos[:limit], 1):
        title = video.get('title', 'Unknown Title')
        view_count = video.get('view_count', 0)
        view_count_updated = video.get('view_count_updated', 'Never')
        
        # Format the timestamp if available
        if view_count_updated and view_count_updated != 'Never':
            from datetime import datetime
            try:
                view_count_updated = datetime.fromisoformat(view_count_updated).strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        print(f"{i}. {title}")
        print(f"   Views: {view_count:,}")
        print(f"   Last Updated: {view_count_updated}")
        print(f"   ID: {video.get('id', 'Unknown')}")
        print()
    
    return 0

def display_top_scored_videos_command(scoring, limit: int = 10) -> int:
    """
    Display top videos by score.
    
    Args:
        scoring: ScoreCalculator instance
        limit: Number of videos to display
        
    Returns:
        Exit code
    """
    # Get current time slot
    current_slot = scoring.get_current_time_slot()
    print(f"\nCurrent time slot: {current_slot}")
    
    # Get top videos for current time slot
    videos = scoring.get_top_videos(time_slot=current_slot, limit=limit)
    
    print(f"\nTop {min(limit, len(videos))} Videos by Score for {current_slot}:")
    print("-" * 80)
    
    for i, video in enumerate(videos, 1):
        title = video.get('title', 'Unknown Title')
        score = video.get('score', 0)
        base_score = video.get('base_score', 0)
        engagement_score = video.get('engagement_score', 0)
        youtube_views = video.get('youtube_views', 0)
        
        print(f"{i}. {title}")
        print(f"   Score: {score:.2f} (Base: {base_score:.2f}, Engagement: {engagement_score:.2f})")
        print(f"   Views: {youtube_views:,}")
        if video.get('is_new_release', False):
            print(f"   [NEW RELEASE]")
        print(f"   ID: {video.get('id', 'Unknown')}")
        print()
    
    return 0