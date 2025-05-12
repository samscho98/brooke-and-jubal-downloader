"""
Audio module package initialization.
"""
# Import statements to make components available from the package
try:
    from audio.player import AudioPlayer
    from audio.queue_manager import QueueManager
    from audio.metadata import MetadataHandler
    
    __all__ = ['AudioPlayer', 'QueueManager', 'MetadataHandler']
except ImportError as e:
    # Log but don't fail if there's an import error
    import logging
    logging.warning(f"Error importing audio components: {str(e)}")
    __all__ = []