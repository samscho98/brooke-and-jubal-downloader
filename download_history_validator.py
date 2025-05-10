#!/usr/bin/env python3
"""
Download History Validator
A diagnostic tool to check the validity of the download history JSON file
and verify paths to audio files.
"""

import os
import json
import argparse
from pathlib import Path

def validate_history(history_file, fix=False):
    """
    Validate the download history file and check if audio files exist
    
    Args:
        history_file: Path to the download history file
        fix: If True, attempt to fix paths and save updated history
    """
    if not os.path.exists(history_file):
        print(f"❌ Error: Download history file not found: {history_file}")
        return
    
    try:
        # Load the history file
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if "videos" not in history:
            print(f"❌ Error: Invalid download history format - missing 'videos' field")
            return
        
        # Track statistics
        total_videos = len(history["videos"])
        existing_files = 0
        missing_files = 0
        playlist_info_count = 0
        playlists_count = 0
        fixed_paths = 0
        
        # Track unique playlists
        playlists = {}
        
        print(f"\n=== Validating Download History: {history_file} ===")
        print(f"Total videos in history: {total_videos}")
        
        # Check each video entry
        for video_id, video_info in history["videos"].items():
            # Check file path
            file_path = video_info.get("file_path")
            if not file_path:
                print(f"⚠️ Warning: Video {video_id} has no file_path")
                missing_files += 1
                continue
            
            # Check if file exists
            if os.path.exists(file_path):
                existing_files += 1
            else:
                missing_files += 1
                
                # Try to fix path if requested
                if fix:
                    fixed_path = None
                    
                    # Try alternate paths
                    file_name = os.path.basename(file_path)
                    
                    # Try looking for file in current directory and subdirectories
                    for root, dirs, files in os.walk('.'):
                        if file_name in files:
                            candidate_path = os.path.join(root, file_name)
                            print(f"🔍 Found potential match for {file_name} at {candidate_path}")
                            if fixed_path is None:
                                fixed_path = candidate_path
                    
                    if fixed_path:
                        print(f"✅ Fixed path for {video_id}: {file_path} -> {fixed_path}")
                        video_info["file_path"] = fixed_path
                        fixed_paths += 1
                        existing_files += 1
                        missing_files -= 1
            
            # Check playlist information
            if "playlist_info" in video_info:
                playlist_info_count += 1
                
                for playlist in video_info["playlist_info"]:
                    playlist_id = playlist.get("id")
                    playlist_name = playlist.get("name")
                    
                    if playlist_id and playlist_name:
                        if playlist_id not in playlists:
                            playlists[playlist_id] = {"name": playlist_name, "count": 0}
                        
                        playlists[playlist_id]["count"] += 1
            
            if "playlists" in video_info and isinstance(video_info["playlists"], list):
                playlists_count += 1
        
        # Print summary
        print("\n=== Download History Summary ===")
        print(f"Total videos: {total_videos}")
        print(f"Files found: {existing_files}")
        print(f"Files missing: {missing_files}")
        print(f"Videos with playlist_info: {playlist_info_count}")
        print(f"Videos with playlists field: {playlists_count}")
        if fix:
            print(f"Fixed paths: {fixed_paths}")
        
        # Print playlist information
        print("\n=== Playlist Information ===")
        print(f"Total unique playlists: {len(playlists)}")
        
        for playlist_id, info in playlists.items():
            print(f"Playlist: {info['name']} (ID: {playlist_id}) - {info['count']} videos")
        
        # Save fixed history if needed
        if fix and fixed_paths > 0:
            backup_file = f"{history_file}.bak"
            print(f"\nCreating backup of original file: {backup_file}")
            
            # Create backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                with open(history_file, 'r', encoding='utf-8') as original:
                    f.write(original.read())
            
            # Save updated history
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved updated history file with {fixed_paths} fixed paths")
        
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {history_file}")
    except Exception as e:
        print(f"❌ Error validating history: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Validate download history JSON file")
    parser.add_argument("history_file", nargs="?", default="gui_app/download_history.json", help="Path to the download history JSON file")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix paths and save updated history")
    
    args = parser.parse_args()
    validate_history(args.history_file, args.fix)

if __name__ == "__main__":
    main()