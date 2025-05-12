#!/usr/bin/env python3
"""
CLI display module.
Handles terminal output formatting and display utilities.
"""
import os
import sys
import logging
from typing import Optional, Dict, List, Any, Union

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional file to log to
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = []
    if log_file:
        # Make sure the directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:  # Only create if there's a directory path
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    handlers.append(logging.StreamHandler())
    
    # Reset any previous configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers
    )

def format_date(date_str: str, input_format: str = "%Y%m%d", 
               output_format: str = "%B %d, %Y") -> str:
    """
    Format a date string from one format to another.
    
    Args:
        date_str: Date string to format
        input_format: Input date format
        output_format: Output date format
        
    Returns:
        Formatted date string or original string if formatting fails
    """
    if not date_str:
        return ""
        
    try:
        from datetime import datetime
        formatted_date = datetime.strptime(date_str, input_format).strftime(output_format)
        return formatted_date
    except (ValueError, TypeError):
        return date_str

def format_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes < 0:
        raise ValueError("Size cannot be negative")
        
    if size_bytes == 0:
        return "0 B"
        
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def format_duration(duration_seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        duration_seconds: Duration in seconds
        
    Returns:
        Human-readable duration string
    """
    if duration_seconds < 0:
        raise ValueError("Duration cannot be negative")
        
    hours, remainder = divmod(int(duration_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def print_header(text: str, char: str = "=", width: int = 80) -> None:
    """
    Print a header with the given text.
    
    Args:
        text: Header text
        char: Character to use for the separator line
        width: Width of the separator line
    """
    print(f"\n{text}")
    print(char * width)

def print_list_item(index: int, title: str, details: Dict[str, Any] = None, 
                   indent: int = 3) -> None:
    """
    Print a list item with title and optional details.
    
    Args:
        index: Item index
        title: Item title
        details: Optional dictionary of key-value details
        indent: Indentation for details
    """
    print(f"{index}. {title}")
    
    if details:
        indent_str = " " * indent
        for key, value in details.items():
            print(f"{indent_str}{key}: {value}")

def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask for confirmation before proceeding with an action.
    
    Args:
        prompt: Prompt to display
        default: Default answer if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default:
        prompt = f"{prompt} [Y/n] "
    else:
        prompt = f"{prompt} [y/N] "
        
    while True:
        choice = input(prompt).lower()
        if choice == "":
            return default
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")