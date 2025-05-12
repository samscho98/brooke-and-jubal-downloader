# Data Module

A data management module for persistent storage, file operations, and configuration management.

## Overview

The `data` module provides functionality for managing persistent data storage, file system operations, and application configuration. It includes classes for handling JSON storage, file operations, and configuration management through INI files.

## Classes and Methods

### StorageInterface

An abstract interface that defines the contract for all storage implementations.

#### Methods

- `load(key=None)`: Loads data from storage.
  - `key`: Optional key to load specific data
  - Returns: Loaded data or None if not found

- `save(data, key=None)`: Saves data to storage.
  - `data`: Data to save
  - `key`: Optional key to save data under
  - Returns: True if saved successfully, False otherwise

- `update(data, key=None)`: Updates existing data in storage.
  - `data`: Data to update with
  - `key`: Optional key to update specific data
  - Returns: True if updated successfully, False otherwise

- `delete(key)`: Deletes data from storage.
  - `key`: Key of data to delete
  - Returns: True if deleted successfully, False otherwise

- `exists(key)`: Checks if data exists in storage.
  - `key`: Key to check for
  - Returns: True if exists, False otherwise

- `list_keys()`: Lists all keys in storage.
  - Returns: List of keys

### JSONStorage

A concrete implementation of `StorageInterface` that stores data in JSON files.

#### Methods

- `__init__(file_path, default_data=None)`: Initializes the JSON storage.
  - `file_path`: Path to the JSON file
  - `default_data`: Default data to use if file doesn't exist

- All methods from `StorageInterface` are implemented

- `_get_nested_value(data, key)`: Gets a value from nested dictionaries using dot notation.
  - `data`: Dictionary to get value from
  - `key`: Key in dot notation (e.g., "parent.child.key")
  - Returns: Value or None if not found

- `_set_nested_value(data, key, value)`: Sets a value in nested dictionaries using dot notation.
  - `data`: Dictionary to set value in
  - `key`: Key in dot notation (e.g., "parent.child.key")
  - `value`: Value to set

- `_deep_update(target, source)`: Deep updates a dictionary.
  - `target`: Target dictionary to update
  - `source`: Source dictionary with updates

### FileManager

Class to handle file operations and organization.

#### Methods

- `__init__(base_dir="data/audio")`: Initializes the file manager.
  - `base_dir`: Base directory for file operations

- `_ensure_dir_exists(directory)`: Creates a directory if it doesn't exist.
  - `directory`: Directory path to create

- `clean_filename(filename)`: Cleans a filename to make it filesystem-safe.
  - `filename`: Original filename
  - Returns: Cleaned filename

- `get_unique_filename(filepath)`: Gets a unique filename by appending a number if the file already exists.
  - `filepath`: Original file path
  - Returns: Unique file path

- `move_file(source, destination, overwrite=False)`: Moves a file from source to destination.
  - `source`: Source file path
  - `destination`: Destination file path
  - `overwrite`: If True, overwrite existing destination file
  - Returns: New file path if successful, None otherwise

- `copy_file(source, destination, overwrite=False)`: Copies a file from source to destination.
  - `source`: Source file path
  - `destination`: Destination file path
  - `overwrite`: If True, overwrite existing destination file
  - Returns: New file path if successful, None otherwise

- `delete_file(filepath)`: Deletes a file.
  - `filepath`: Path to the file to delete
  - Returns: True if successful, False otherwise

- `list_files(directory=None, pattern=None)`: Lists files in a directory, optionally filtered by pattern.
  - `directory`: Directory to list files from (default: base_dir)
  - `pattern`: Glob pattern to filter files
  - Returns: List of file paths

- `get_file_info(filepath)`: Gets information about a file.
  - `filepath`: Path to the file
  - Returns: Dictionary with file information

- `create_organized_path(filename, subfolder=None)`: Creates an organized path structure for a file.
  - `filename`: Original filename
  - `subfolder`: Optional subfolder within base_dir
  - Returns: Organized file path

- `create_temp_directory()`: Creates a temporary directory for processing.
  - Returns: Path to the temporary directory

- `cleanup_temp_directory(temp_dir)`: Cleans up a temporary directory.
  - `temp_dir`: Path to the temporary directory
  - Returns: True if successful, False otherwise

- `get_directory_size(directory)`: Gets the total size of a directory and its contents in bytes.
  - `directory`: Directory path
  - Returns: Size in bytes

- `list_directories(parent_dir=None)`: Lists all subdirectories in a directory.
  - `parent_dir`: Parent directory (default: base_dir)
  - Returns: List of directory paths

### ConfigHandler

Class to handle application configuration loading and saving.

#### Default Configuration

The `ConfigHandler` includes default configuration settings for:
- General settings (output directory, check interval, max downloads)
- Audio settings (format, bitrate, normalization)
- Player settings (default playlist, history, auto-normalize)
- Scoring settings (enable scoring, score decay, new content boost)
- Logging settings (level, file, console output)

#### Methods

- `__init__(config_file="config.ini")`: Initializes the config handler.
  - `config_file`: Path to the configuration file

- `_create_default_config()`: Creates a default configuration file.

- `_load_config()`: Loads configuration from file, creating default if not exists.

- `save_config()`: Saves configuration to file.
  - Returns: True if successful, False otherwise

- `get(section, option, fallback=None)`: Gets a configuration value.
  - `section`: Configuration section
  - `option`: Option name
  - `fallback`: Value to return if section/option not found
  - Returns: Configuration value as string

- `getint(section, option, fallback=None)`: Gets a configuration value as integer.
  - `section`: Configuration section
  - `option`: Option name
  - `fallback`: Value to return if section/option not found
  - Returns: Configuration value as integer

- `getfloat(section, option, fallback=None)`: Gets a configuration value as float.
  - `section`: Configuration section
  - `option`: Option name
  - `fallback`: Value to return if section/option not found
  - Returns: Configuration value as float

- `getboolean(section, option, fallback=None)`: Gets a configuration value as boolean.
  - `section`: Configuration section
  - `option`: Option name
  - `fallback`: Value to return if section/option not found
  - Returns: Configuration value as boolean

- `set(section, option, value)`: Sets a configuration value.
  - `section`: Configuration section
  - `option`: Option name
  - `value`: New value

- `get_all()`: Gets all configuration values.
  - Returns: Dictionary containing all configuration values

- `get_section(section)`: Gets all options in a section.
  - `section`: Section name
  - Returns: Dictionary with option names and values

- `has_section(section)`: Checks if a section exists.
  - `section`: Section name
  - Returns: True if section exists, False otherwise

- `has_option(section, option)`: Checks if an option exists in a section.
  - `section`: Section name
  - `option`: Option name
  - Returns: True if option exists, False otherwise

- `remove_option(section, option)`: Removes an option from a section.
  - `section`: Section name
  - `option`: Option name
  - Returns: True if removed, False otherwise

- `remove_section(section)`: Removes a section.
  - `section`: Section name
  - Returns: True if removed, False otherwise

- `reset_to_default(section=None, option=None)`: Resets configuration to default values.
  - `section`: Optional section to reset (None for all)
  - `option`: Optional option to reset (None for all in section)
  - Returns: True if successful, False otherwise

## Usage

The data module is used for:
- Persisting application data in JSON format
- Managing file operations for downloaded content
- Handling application configuration

### Example: Working with Config

```python
from data.config_manager import ConfigHandler

# Load configuration
config = ConfigHandler("config.ini")

# Get configuration values
output_dir = config.get("general", "output_directory")
audio_format = config.get("audio", "format")
normalize = config.getboolean("audio", "normalize_audio")

# Set configuration values
config.set("audio", "bitrate", "320k")
config.save_config()
```

### Example: Working with Files

```python
from data.file_manager import FileManager

# Initialize file manager
file_mgr = FileManager("data/audio")

# Create organized file path
path = file_mgr.create_organized_path("My Song.mp3", "playlist1")

# List audio files
mp3_files = file_mgr.list_files(pattern="*.mp3")
```

### Example: Working with Storage

```python
from data.json_storage import JSONStorage

# Initialize storage
storage = JSONStorage("data/playlists.json")

# Save data
playlist_data = {"name": "My Playlist", "tracks": [...]}
storage.save(playlist_data, "playlists.my_playlist")

# Load data
my_playlist = storage.load("playlists.my_playlist")
```