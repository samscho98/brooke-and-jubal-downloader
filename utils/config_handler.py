"""
Configuration handler module.
Manages loading and saving of application configuration.
"""
import os
import logging
import configparser
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ConfigHandler:
    """Class to handle application configuration loading and saving."""
    
    DEFAULT_CONFIG = {
        "general": {
            "output_directory": "data/audio",
            "check_interval": "24",  # hours
            "max_downloads": "10",   # per run
        },
        "audio": {
            "format": "mp3",
            "bitrate": "192k",
            "normalize_audio": "True",
            "target_level": "-18.0",  # dB
        },
        "logging": {
            "level": "INFO",
            "file": "app.log",
            "console": "True",
        }
    }
    
    def __init__(self, config_file: str = "config.ini"):
        """
        Initialize the config handler.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        for section, options in self.DEFAULT_CONFIG.items():
            self.config[section] = options
            
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            logger.info(f"Created default configuration file: {self.config_file}")
        except Exception as e:
            logger.error(f"Error creating default configuration: {str(e)}")
    
    def _load_config(self) -> None:
        """Load configuration from file, creating default if not exists."""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                logger.info(f"Loaded configuration from: {self.config_file}")
                
                # Validate required sections and add missing ones
                for section, options in self.DEFAULT_CONFIG.items():
                    if not self.config.has_section(section):
                        logger.warning(f"Missing section [{section}] in config, adding default")
                        self.config[section] = options
                    else:
                        # Add any missing options with default values
                        for option, value in options.items():
                            if not self.config.has_option(section, option):
                                logger.warning(f"Missing option {option} in [{section}], adding default")
                                self.config[section][option] = value
                
                # Save if any changes were made
                self.save_config()
                    
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}. Using defaults.")
                self._create_default_config()
        else:
            logger.info("Configuration file not found. Creating default.")
            self._create_default_config()
    
    def save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a backup of the existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.bak"
                try:
                    import shutil
                    shutil.copy2(self.config_file, backup_file)
                    logger.info(f"Created backup of config file: {backup_file}")
                except Exception as e:
                    logger.warning(f"Failed to create config backup: {str(e)}")
            
            # Save the updated config
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            logger.info(f"Saved configuration to: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            option: Option name
            fallback: Value to return if section/option not found
            
        Returns:
            Configuration value as string
        """
        return self.config.get(section, option, fallback=fallback)
    
    def getint(self, section: str, option: str, fallback: Optional[int] = None) -> int:
        """
        Get a configuration value as integer.
        
        Args:
            section: Configuration section
            option: Option name
            fallback: Value to return if section/option not found
            
        Returns:
            Configuration value as integer
        """
        return self.config.getint(section, option, fallback=fallback)
    
    def getfloat(self, section: str, option: str, fallback: Optional[float] = None) -> float:
        """
        Get a configuration value as float.
        
        Args:
            section: Configuration section
            option: Option name
            fallback: Value to return if section/option not found
            
        Returns:
            Configuration value as float
        """
        return self.config.getfloat(section, option, fallback=fallback)
    
    def getboolean(self, section: str, option: str, fallback: Optional[bool] = None) -> bool:
        """
        Get a configuration value as boolean.
        
        Args:
            section: Configuration section
            option: Option name
            fallback: Value to return if section/option not found
            
        Returns:
            Configuration value as boolean
        """
        return self.config.getboolean(section, option, fallback=fallback)
    
    def set(self, section: str, option: str, value: str) -> None:
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            option: Option name
            value: New value
        """
        # Create section if it doesn't exist
        if not self.config.has_section(section):
            self.config.add_section(section)
            
        self.config[section][option] = str(value)
    
    def get_all(self) -> Dict[str, Dict[str, str]]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary containing all configuration values
        """
        result = {}
        for section in self.config.sections():
            result[section] = {}
            for option in self.config[section]:
                result[section][option] = self.config[section][option]
        return result