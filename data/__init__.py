"""
Data management package for persistent storage operations.
"""
from data.config_manager import ConfigHandler as ConfigManager
from data.file_manager import FileManager
from data.json_storage import JSONStorage
from data.storage import StorageInterface

__all__ = ['ConfigManager', 'FileManager', 'JSONStorage', 'StorageInterface']