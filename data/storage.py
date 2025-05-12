"""
Storage interface module.
Defines the abstract interface for data storage implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class StorageInterface(ABC):
    """Abstract interface for data storage implementations."""
    
    @abstractmethod
    def load(self, key: Optional[str] = None) -> Any:
        """
        Load data from storage.
        
        Args:
            key: Optional key to load specific data
            
        Returns:
            Loaded data or None if not found
        """
        pass
    
    @abstractmethod
    def save(self, data: Any, key: Optional[str] = None) -> bool:
        """
        Save data to storage.
        
        Args:
            data: Data to save
            key: Optional key to save data under
            
        Returns:
            True if saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def update(self, data: Any, key: Optional[str] = None) -> bool:
        """
        Update existing data in storage.
        
        Args:
            data: Data to update with
            key: Optional key to update specific data
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete data from storage.
        
        Args:
            key: Key of data to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if data exists in storage.
        
        Args:
            key: Key to check for
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_keys(self) -> List[str]:
        """
        List all keys in storage.
        
        Returns:
            List of keys
        """
        pass

class StorageError(Exception):
    """Exception raised for storage-related errors."""
    pass