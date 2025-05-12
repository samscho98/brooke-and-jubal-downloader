"""
Logger module providing logging configuration.
"""
import os
import logging
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    """
    # Set up logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Basic configuration
    logging_config = {
        'level': numeric_level,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        logging_config['filename'] = log_file
        logging_config['filemode'] = 'a'  # Append mode
        
    # Apply configuration
    logging.basicConfig(**logging_config)
    
    # If no log file is specified, add a console handler
    if not log_file:
        console = logging.StreamHandler()
        console.setLevel(numeric_level)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    
    logging.info(f"Logging initialized at level {log_level}")

# Test function
if __name__ == "__main__":
    setup_logging(log_level="DEBUG", log_file="logs/test.log")
    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")