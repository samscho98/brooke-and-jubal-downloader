"""
File manager module.
Handles file operations, path management, and media file processing.
"""
import os
import logging
import shutil
from typing import List, Optional, Tuple
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class FileManager:
    """Class to handle file operations and management."""
    
    def __init__(self, base_dir: str = "data/audio"):
        """
        Initialize the file manager.
        
        Args:
            base_dir: Base directory for file operations
        """
        self.base_dir = base_dir
        self._ensure_dir_exists(base_dir)
    
    def _ensure_dir_exists(self, directory: str) -> None:
        """
        Create a directory if it doesn't exist.
        
        Args:
            directory: Directory path to create
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def clean_filename(self, filename: str) -> str:
        """
        Clean a filename to make it filesystem-safe.
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Replace invalid characters with underscores
        clean = re.sub(r'[\\/*?:"<>|]', '_', filename)
        
        # Remove leading/trailing whitespace and dots
        clean = clean.strip().strip('.')
        
        # Limit length (most filesystems have a 255 character limit)
        if len(clean) > 240:
            base, ext = os.path.splitext(clean)
            clean = base[:240 - len(ext)] + ext
        
        return clean
    
    def get_unique_filename(self, filepath: str) -> str:
        """
        Get a unique filename by appending a number if the file already exists.
        
        Args:
            filepath: Original file path
            
        Returns:
            Unique file path
        """
        if not os.path.exists(filepath):
            return filepath
            
        directory, filename = os.path.split(filepath)
        name, extension = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filepath = os.path.join(directory, f"{name}_{counter}{extension}")
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1
    
    def move_file(self, source: str, destination: str, 
                 overwrite: bool = False) -> Optional[str]:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: If True, overwrite existing destination file
            
        Returns:
            New file path if successful, None otherwise
        """
        if not os.path.exists(source):
            logger.error(f"Source file not found: {source}")
            return None
            
        try:
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            self._ensure_dir_exists(dest_dir)
            
            # Check if destination exists and handle accordingly
            if os.path.exists(destination):
                if overwrite:
                    os.remove(destination)
                    logger.info(f"Removed existing file: {destination}")
                else:
                    destination = self.get_unique_filename(destination)
                    logger.info(f"Using unique filename: {destination}")
            
            # Move the file
            shutil.move(source, destination)
            logger.info(f"Moved file from {source} to {destination}")
            return destination
            
        except Exception as e:
            logger.error(f"Error moving file: {str(e)}")
            return None
    
    def copy_file(self, source: str, destination: str, 
                 overwrite: bool = False) -> Optional[str]:
        """
        Copy a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: If True, overwrite existing destination file
            
        Returns:
            New file path if successful, None otherwise
        """
        if not os.path.exists(source):
            logger.error(f"Source file not found: {source}")
            return None
            
        try:
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            self._ensure_dir_exists(dest_dir)
            
            # Check if destination exists and handle accordingly
            if os.path.exists(destination):
                if overwrite:
                    os.remove(destination)
                    logger.info(f"Removed existing file: {destination}")
                else:
                    destination = self.get_unique_filename(destination)
                    logger.info(f"Using unique filename: {destination}")
            
            # Copy the file
            shutil.copy2(source, destination)
            logger.info(f"Copied file from {source} to {destination}")
            return destination
            
        except Exception as e:
            logger.error(f"Error copying file: {str(e)}")
            return None
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file.
        
        Args:
            filepath: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(filepath):
            logger.warning(f"File not found for deletion: {filepath}")
            return False
            
        try:
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def list_files(self, directory: Optional[str] = None, 
                  pattern: Optional[str] = None) -> List[str]:
        """
        List files in a directory, optionally filtered by pattern.
        
        Args:
            directory: Directory to list files from (default: base_dir)
            pattern: Glob pattern to filter files
            
        Returns:
            List of file paths
        """
        if directory is None:
            directory = self.base_dir
            
        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            return []
            
        try:
            if pattern:
                return list(str(p) for p in Path(directory).glob(pattern))
            else:
                return [os.path.join(directory, f) for f in os.listdir(directory) 
                        if os.path.isfile(os.path.join(directory, f))]
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def get_file_info(self, filepath: str) -> Optional[dict]:
        """
        Get information about a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with file information
        """
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return None
            
        try:
            stat_info = os.stat(filepath)
            file_info = {
                "path": filepath,
                "name": os.path.basename(filepath),
                "directory": os.path.dirname(filepath),
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "extension": os.path.splitext(filepath)[1].lower(),
            }
            return file_info
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None
    
    def create_organized_path(self, filename: str, subfolder: Optional[str] = None) -> str:
        """
        Create an organized path structure for a file.
        
        Args:
            filename: Original filename
            subfolder: Optional subfolder within base_dir
            
        Returns:
            Organized file path
        """
        clean_name = self.clean_filename(filename)
        
        if subfolder:
            target_dir = os.path.join(self.base_dir, subfolder)
        else:
            target_dir = self.base_dir
            
        self._ensure_dir_exists(target_dir)
        return os.path.join(target_dir, clean_name)
    
    def create_temp_directory(self) -> str:
        """
        Create a temporary directory for processing.
        
        Returns:
            Path to the temporary directory
        """
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="ytdownloader_")
        logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir
    
    def cleanup_temp_directory(self, temp_dir: str) -> bool:
        """
        Clean up a temporary directory.
        
        Args:
            temp_dir: Path to the temporary directory
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(temp_dir):
            return True
            
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"Removed temporary directory: {temp_dir}")
            return True
        except Exception as e:
            logger.error(f"Error removing temporary directory: {str(e)}")
            return False