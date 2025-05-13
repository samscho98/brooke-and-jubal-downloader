"""
Path utilities for consistent file system access.
"""
import os
import sys
from typing import List, Optional


def clean_output_path(path: str) -> str:
    """
    Clean a file or directory path to prevent duplication issues.
    """
    # Normalize path separators to OS-specific format
    import os
    normalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    
    # Check for data/audio duplication
    data_audio_pattern = f"data{os.sep}audio"
    
    if normalized_path.count(data_audio_pattern) > 1:
        # Split path by the pattern
        parts = normalized_path.split(data_audio_pattern)
        
        # Keep only the first occurrence and the last part
        if len(parts) >= 2:
            cleaned_path = data_audio_pattern + parts[-1]
            return cleaned_path
    
    return normalized_path

def get_path(*args: str) -> str:
    """
    Get an absolute path relative to the application root directory.
    
    Args:
        *args: Path components to join (e.g., "data", "download_history.json")
        
    Returns:
        Absolute path from the application root
    
    Example:
        get_path("data", "download_history.json") -> "/path/to/app/data/download_history.json"
    """
    # Determine the application root directory
    if getattr(sys, 'frozen', False):
        # If running as compiled executable (PyInstaller)
        app_root = os.path.dirname(sys.executable)
    else:
        # If running as script, go up to the application root
        # Adjust the number of parent directories as needed based on where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.dirname(current_dir)  # Go up one level
    
    # Join the app root with the provided path components
    return os.path.join(app_root, *args)

def ensure_dir_exists(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        import logging
        logging.error(f"Error creating directory {path}: {str(e)}")
        return False

def get_data_path(filename: Optional[str] = None) -> str:
    """
    Get the path to a file in the data directory.
    Creates the data directory if it doesn't exist.
    
    Args:
        filename: Optional filename within the data directory
        
    Returns:
        Absolute path to the data directory or file
    """
    data_dir = get_path("data")
    ensure_dir_exists(data_dir)
    
    if filename:
        return os.path.join(data_dir, filename)
    return data_dir

def get_audio_path(filename: Optional[str] = None) -> str:
    """
    Get the path to a file in the audio directory.
    Creates the audio directory if it doesn't exist.
    
    Args:
        filename: Optional filename within the audio directory
        
    Returns:
        Absolute path to the audio directory or file
    """
    audio_dir = get_path("data", "audio")
    ensure_dir_exists(audio_dir)
    
    if filename:
        return os.path.join(audio_dir, filename)
    return audio_dir

def get_logs_path(filename: Optional[str] = None) -> str:
    """
    Get the path to a file in the logs directory.
    Creates the logs directory if it doesn't exist.
    
    Args:
        filename: Optional filename within the logs directory
        
    Returns:
        Absolute path to the logs directory or file
    """
    logs_dir = get_path("logs")
    ensure_dir_exists(logs_dir)
    
    if filename:
        return os.path.join(logs_dir, filename)
    return logs_dir