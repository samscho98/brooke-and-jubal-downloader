"""
JSON storage module.
Implements storage interface using JSON files.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from data.storage import StorageInterface, StorageError

logger = logging.getLogger(__name__)

class JSONStorage(StorageInterface):
    """Storage implementation using JSON files."""
    
    def __init__(self, file_path: str, default_data: Optional[Dict] = None):
        """
        Initialize the JSON storage.
        
        Args:
            file_path: Path to the JSON file
            default_data: Default data to use if file doesn't exist
        """
        self.file_path = file_path
        self.default_data = default_data or {}
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Create file with default data if it doesn't exist
        if not os.path.exists(file_path):
            self.save(self.default_data)
            logger.info(f"Created new JSON file with default data: {file_path}")
    
    def load(self, key: Optional[str] = None) -> Any:
        """
        Load data from the JSON file.
        
        Args:
            key: Optional key to load specific data
            
        Returns:
            Loaded data or None if not found
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if key is not None:
                return self._get_nested_value(data, key)
            return data
            
        except FileNotFoundError:
            logger.warning(f"File not found: {self.file_path}. Using default data.")
            return self.default_data if key is None else self._get_nested_value(self.default_data, key)
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file: {self.file_path}")
            return self.default_data if key is None else self._get_nested_value(self.default_data, key)
            
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}")
            raise StorageError(f"Error loading JSON file: {str(e)}")
    
    def save(self, data: Any, key: Optional[str] = None) -> bool:
        """
        Save data to the JSON file.
        
        Args:
            data: Data to save
            key: Optional key to save data under
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # If key is provided, update only that part of the data
            if key is not None:
                current_data = self.load()
                self._set_nested_value(current_data, key, data)
                data = current_data
            
            # Add last_updated timestamp
            if isinstance(data, dict):
                data["last_updated"] = datetime.now().isoformat()
            
            # Save to file with pretty printing
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved data to JSON file: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to JSON file: {str(e)}")
            return False
    
    def update(self, data: Any, key: Optional[str] = None) -> bool:
        """
        Update existing data in the JSON file.
        
        Args:
            data: Data to update with
            key: Optional key to update specific data
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            current_data = self.load()
            
            if key is not None:
                self._set_nested_value(current_data, key, data)
            elif isinstance(data, dict) and isinstance(current_data, dict):
                # Deep update dictionary
                self._deep_update(current_data, data)
            else:
                # Replace entire data
                current_data = data
            
            # Add last_updated timestamp
            if isinstance(current_data, dict):
                current_data["last_updated"] = datetime.now().isoformat()
            
            # Save to file with pretty printing
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Updated data in JSON file: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating JSON file: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete data from the JSON file.
        
        Args:
            key: Key of data to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            current_data = self.load()
            
            # Handle nested keys
            keys = key.split('.')
            
            if len(keys) == 1:
                # Simple key
                if keys[0] in current_data:
                    del current_data[keys[0]]
                else:
                    logger.warning(f"Key not found for deletion: {key}")
                    return False
            else:
                # Nested key
                parent = current_data
                for k in keys[:-1]:
                    if k not in parent:
                        logger.warning(f"Key not found for deletion: {key}")
                        return False
                    parent = parent[k]
                
                if keys[-1] in parent:
                    del parent[keys[-1]]
                else:
                    logger.warning(f"Key not found for deletion: {key}")
                    return False
            
            # Add last_updated timestamp
            if isinstance(current_data, dict):
                current_data["last_updated"] = datetime.now().isoformat()
            
            # Save to file with pretty printing
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Deleted key {key} from JSON file: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from JSON file: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the JSON file.
        
        Args:
            key: Key to check for
            
        Returns:
            True if exists, False otherwise
        """
        try:
            data = self.load()
            
            # Handle nested keys
            keys = key.split('.')
            current = data
            
            for k in keys:
                if not isinstance(current, dict) or k not in current:
                    return False
                current = current[k]
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking key existence in JSON file: {str(e)}")
            return False
    
    def list_keys(self) -> List[str]:
        """
        List all top-level keys in the JSON file.
        
        Returns:
            List of keys
        """
        try:
            data = self.load()
            
            if isinstance(data, dict):
                return list(data.keys())
            else:
                logger.warning("JSON data is not a dictionary")
                return []
                
        except Exception as e:
            logger.error(f"Error listing keys in JSON file: {str(e)}")
            return []
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """
        Get a value from nested dictionaries using dot notation.
        
        Args:
            data: Dictionary to get value from
            key: Key in dot notation (e.g., "parent.child.key")
            
        Returns:
            Value or None if not found
        """
        keys = key.split('.')
        current = data
        
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return None
            current = current[k]
        
        return current
    
    def _set_nested_value(self, data: Dict, key: str, value: Any) -> None:
        """
        Set a value in nested dictionaries using dot notation.
        
        Args:
            data: Dictionary to set value in
            key: Key in dot notation (e.g., "parent.child.key")
            value: Value to set
        """
        keys = key.split('.')
        current = data
        
        # Navigate to the parent of the leaf key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value at the leaf key
        current[keys[-1]] = value
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """
        Deep update a dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with updates
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value