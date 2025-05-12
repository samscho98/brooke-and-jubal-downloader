"""
Application updater module.
Handles checking for updates and updating the application from GitHub.
"""
import os
import sys
import logging
import tempfile
import shutil
import subprocess
import json
import time
from typing import Dict, Optional, Tuple, List
import urllib.request
import zipfile
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class Updater:
    """Class to handle application updates from GitHub."""
    
    def __init__(self, repo_owner: str = "samscho98", 
                repo_name: str = "youtube-playlist-downloader",
                current_version: str = "1.0.0"):
        """
        Initialize the updater.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            current_version: Current version of the application
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.base_url = f"https://github.com/{repo_owner}/{repo_name}"
        
        # Define data files that should be preserved during updates
        self.preserved_paths = [
            os.path.join("gui_app", "playlists.json"),
            os.path.join("gui_app", "download_history.json"),
            os.path.join("gui_app", "video_scores.json"),
            os.path.join("gui_app", "config.ini")
        ]
    
    def check_for_updates(self) -> Tuple[bool, str, str]:
        """
        Check if updates are available.
        
        Returns:
            Tuple of (update_available, latest_version, release_notes)
        """
        try:
            # Get latest release info from GitHub API
            logger.info(f"Checking for updates from {self.api_url}/releases/latest")
            
            request = urllib.request.Request(
                f"{self.api_url}/releases/latest",
                headers={
                    "User-Agent": f"{self.repo_name} Updater"
                }
            )
            
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            latest_version = data.get("tag_name", "").lstrip("v")
            release_notes = data.get("body", "No release notes available")
            
            # Compare versions
            update_available = self._compare_versions(latest_version)
            
            if update_available:
                logger.info(f"Update available: {latest_version} (current: {self.current_version})")
            else:
                logger.info(f"No updates available. Current version: {self.current_version}, Latest: {latest_version}")
            
            return update_available, latest_version, release_notes
            
        except Exception as e:
            logger.error(f"Error checking for updates: {str(e)}")
            return False, "", f"Error checking for updates: {str(e)}"
    
    def _compare_versions(self, latest_version: str) -> bool:
        """
        Compare version strings to determine if update is needed.
        
        Args:
            latest_version: Latest version from GitHub
            
        Returns:
            True if update is available, False otherwise
        """
        try:
            if not latest_version:
                return False
                
            # Parse version strings into components
            current_parts = list(map(int, re.findall(r'\d+', self.current_version)))
            latest_parts = list(map(int, re.findall(r'\d+', latest_version)))
            
            # Pad shorter version with zeros
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            
            # Compare version components
            for i in range(len(current_parts)):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False
            
            # Versions are equal
            return False
            
        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            # Be safe and indicate no update if we can't parse versions
            return False
    
    def download_update(self, version: str = "") -> Optional[str]:
        """
        Download the latest release from GitHub.
        
        Args:
            version: Specific version to download (empty for latest)
            
        Returns:
            Path to downloaded zip file or None if download failed
        """
        try:
            # Determine download URL
            if version:
                download_url = f"{self.base_url}/archive/refs/tags/v{version}.zip"
            else:
                download_url = f"{self.base_url}/archive/refs/heads/main.zip"
            
            logger.info(f"Downloading update from {download_url}")
            
            # Create temporary directory for download
            temp_dir = tempfile.mkdtemp(prefix="ytdownloader_update_")
            zip_path = os.path.join(temp_dir, f"{self.repo_name}.zip")
            
            # Download the zip file
            urllib.request.urlretrieve(download_url, zip_path, self._download_progress)
            
            logger.info(f"Update downloaded to {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error downloading update: {str(e)}")
            return None
    
    def _download_progress(self, block_num, block_size, total_size):
        """
        Callback for download progress.
        
        Args:
            block_num: Current block number
            block_size: Size of each block
            total_size: Total download size
        """
        # Calculate progress percentage
        downloaded = block_num * block_size
        progress = min(100, int(downloaded * 100 / total_size if total_size > 0 else 0))
        
        # Log progress at intervals
        if block_num % 50 == 0:
            logger.info(f"Download progress: {progress}% ({downloaded}/{total_size} bytes)")
    
    def _backup_preserved_files(self, app_dir: str) -> Dict[str, str]:
        """
        Create backups of important data files.
        
        Args:
            app_dir: Application directory path
            
        Returns:
            Dictionary mapping original paths to backup paths
        """
        backup_files = {}
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Create a temp directory for data backups
        backup_dir = os.path.join(app_dir, f"data_backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        
        logger.info(f"Backing up data files to {backup_dir}")
        
        # Backup each preserved file
        for rel_path in self.preserved_paths:
            full_path = os.path.join(app_dir, rel_path)
            if os.path.exists(full_path):
                # Get filename only
                filename = os.path.basename(rel_path)
                # Create backup path
                backup_path = os.path.join(backup_dir, filename)
                
                # Copy the file
                try:
                    shutil.copy2(full_path, backup_path)
                    backup_files[full_path] = backup_path
                    logger.info(f"Backed up {full_path} to {backup_path}")
                except Exception as e:
                    logger.error(f"Failed to backup {full_path}: {str(e)}")
        
        return backup_files
    
    def _restore_preserved_files(self, backup_files: Dict[str, str]) -> None:
        """
        Restore data files from backups.
        
        Args:
            backup_files: Dictionary mapping original paths to backup paths
        """
        logger.info("Restoring preserved files from backups")
        for original_path, backup_path in backup_files.items():
            if os.path.exists(backup_path):
                try:
                    # Make sure directory exists
                    os.makedirs(os.path.dirname(original_path), exist_ok=True)
                    
                    # Copy backup back to original location
                    shutil.copy2(backup_path, original_path)
                    logger.info(f"Restored {original_path} from {backup_path}")
                except Exception as e:
                    logger.error(f"Failed to restore {original_path}: {str(e)}")
    
    def install_update(self, zip_path: str) -> bool:
        """
        Install the downloaded update.
        
        Args:
            zip_path: Path to the downloaded zip file
            
        Returns:
            True if update was successful, False otherwise
        """
        if not os.path.exists(zip_path):
            logger.error(f"Update file not found: {zip_path}")
            return False
        
        try:
            # Create temporary directory for extraction
            extract_dir = tempfile.mkdtemp(prefix="ytdownloader_extract_")
            logger.info(f"Extracting update to {extract_dir}")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the extracted directory
            extracted_items = os.listdir(extract_dir)
            if not extracted_items:
                logger.error("No files found in downloaded update")
                return False
                
            # Usually, GitHub archives contain a single directory with the repo name
            extracted_dir = os.path.join(extract_dir, extracted_items[0])
            
            # Get the application directory
            app_dir = self._get_app_directory()
            if not app_dir:
                logger.error("Could not determine application directory")
                return False
            
            # Backup current version
            backup_dir = self._backup_current_version(app_dir)
            if not backup_dir:
                logger.error("Failed to create backup")
                return False
            
            # Backup preserved files BEFORE updating
            backup_files = self._backup_preserved_files(app_dir)
            if not backup_files:
                logger.warning("No data files were backed up")
            
            # Copy files from extracted directory to application directory
            logger.info(f"Copying updated files to {app_dir}")
            self._copy_update_files(extracted_dir, app_dir)
            
            # Restore preserved files AFTER updating
            self._restore_preserved_files(backup_files)
            
            # Clean up
            try:
                shutil.rmtree(extract_dir)
                os.remove(zip_path)
                logger.info("Cleaned up temporary files")
            except Exception as e:
                logger.warning(f"Error cleaning up: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error installing update: {str(e)}")
            return False
    
    def _get_app_directory(self) -> Optional[str]:
        """
        Get the application directory.
        
        Returns:
            Path to the application directory or None if cannot be determined
        """
        try:
            # Get the parent directory of this file
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            return app_dir
            
        except Exception as e:
            logger.error(f"Error determining application directory: {str(e)}")
            return None
    
    def _backup_current_version(self, app_dir: str) -> Optional[str]:
        """
        Create a backup of the current version.
        
        Args:
            app_dir: Path to the application directory
            
        Returns:
            Path to the backup directory or None if backup failed
        """
        try:
            # Create backup directory
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(app_dir, f"backup_{timestamp}")
            logger.info(f"Creating backup in {backup_dir}")
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup essential files and directories
            essential_items = self._get_essential_items()
            
            for item in essential_items:
                src_path = os.path.join(app_dir, item)
                if os.path.exists(src_path):
                    dst_path = os.path.join(backup_dir, item)
                    
                    # Create parent directories if needed
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
            
            logger.info(f"Backup created in {backup_dir}")
            return backup_dir
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return None
    
    def _get_essential_items(self) -> List[str]:
        """
        Get a list of essential items to backup.
        
        Returns:
            List of essential file/directory paths relative to app directory
        """
        # Include essential Python files, excluding data directories
        essential_items = [
            "downloader",
            "gui_app",
            "utils",
            "main.py",
            "run_console.bat",
            "run_gui.bat",
            "config.ini",
            "installer.py",
            "README.md",
            "requirements.txt"
        ]
        
        # Don't include large data or generated directories
        excluded_items = [
            "data",
            "venv",
            "__pycache__",
            ".git"
        ]
        
        return essential_items
    
    def _is_path_preserved(self, path: str, app_dir: str) -> bool:
        """
        Check if a path should be preserved during update.
        
        Args:
            path: Absolute path to check
            app_dir: Application directory path
            
        Returns:
            True if the path should be preserved, False otherwise
        """
        # Convert to relative path for comparison
        try:
            rel_path = os.path.relpath(path, app_dir)
            
            # Check if this path matches any of our preserved paths
            for preserved in self.preserved_paths:
                if rel_path == preserved:
                    return True
            
            return False
        except:
            # If we can't get a relative path, assume not preserved
            return False
    
    def _copy_update_files(self, src_dir: str, dst_dir: str) -> None:
        """
        Copy update files to application directory.
        
        Args:
            src_dir: Source directory with extracted files
            dst_dir: Destination application directory
        """
        # Get the list of excluded directories and files
        excluded_items = [
            "data",
            "venv",
            "__pycache__",
            ".git",
            ".github",
            ".gitignore",
            ".env"
        ]
        
        # Copy all files and directories from source to destination
        for item in os.listdir(src_dir):
            # Skip excluded items
            if item in excluded_items:
                continue
                
            src_item = os.path.join(src_dir, item)
            dst_item = os.path.join(dst_dir, item)
            
            if os.path.isdir(src_item):
                # For directories, we need to handle recursively
                self._copy_directory_with_preservation(src_item, dst_item, dst_dir)
                logger.info(f"Copied directory: {item}")
            else:
                # For files, check if it's a preserved file
                if not self._is_path_preserved(dst_item, dst_dir):
                    # Remove existing file if it exists
                    if os.path.exists(dst_item):
                        os.remove(dst_item)
                    
                    # Copy the file
                    shutil.copy2(src_item, dst_item)
                    logger.info(f"Copied file: {item}")
                else:
                    logger.info(f"Preserved file: {item}")
    
    def _copy_directory_with_preservation(self, src_dir: str, dst_dir: str, app_dir: str) -> None:
        """
        Copy a directory while preserving specified files.
        
        Args:
            src_dir: Source directory
            dst_dir: Destination directory
            app_dir: Application root directory
        """
        # Create destination directory if it doesn't exist
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        # Copy all files and subdirectories
        for item in os.listdir(src_dir):
            src_item = os.path.join(src_dir, item)
            dst_item = os.path.join(dst_dir, item)
            
            if os.path.isdir(src_item):
                # Recursively copy subdirectories
                self._copy_directory_with_preservation(src_item, dst_item, app_dir)
            else:
                # Only copy if it's not a preserved file
                if not self._is_path_preserved(dst_item, app_dir):
                    # Remove existing file if it exists
                    if os.path.exists(dst_item):
                        os.remove(dst_item)
                    
                    # Copy the file
                    shutil.copy2(src_item, dst_item)
                    logger.debug(f"Copied file: {os.path.relpath(dst_item, app_dir)}")
                else:
                    logger.info(f"Preserved file: {os.path.relpath(dst_item, app_dir)}")
    
    def update_application(self, auto_restart: bool = False) -> bool:
        """
        Check for updates and install if available.
        
        Args:
            auto_restart: Whether to automatically restart the application
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Check for updates
            update_available, latest_version, release_notes = self.check_for_updates()
            
            if not update_available:
                logger.info("No updates available.")
                return False
            
            # Download the update
            zip_path = self.download_update(latest_version)
            if not zip_path:
                logger.error("Failed to download update.")
                return False
            
            # Install the update
            success = self.install_update(zip_path)
            if not success:
                logger.error("Failed to install update.")
                return False
            
            logger.info(f"Successfully updated to version {latest_version}")
            
            # Restart the application if requested
            if auto_restart:
                self._restart_application()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating application: {str(e)}")
            return False
    
    def _restart_application(self) -> None:
        """
        Restart the application.
        """
        try:
            logger.info("Restarting application...")
            
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                # Running as script
                args = [sys.executable] + sys.argv
                subprocess.Popen(args)
                sys.exit(0)
                
        except Exception as e:
            logger.error(f"Error restarting application: {str(e)}")