"""
Audio converter module.
Handles converting between audio formats and processing audio files.
"""
import os
import logging
from typing import Optional
import subprocess
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioConverter:
    """Class to handle audio conversion operations."""
    
    SUPPORTED_FORMATS = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']
    
    @staticmethod
    def convert_audio(input_file: str, output_format: str = "mp3", output_dir: Optional[str] = None, 
                      bitrate: str = "192k") -> Optional[str]:
        """
        Convert an audio file to the specified format.
        
        Args:
            input_file: Path to the input audio file
            output_format: Desired output format (mp3, wav, ogg, etc.)
            output_dir: Directory to save the output file (defaults to same as input)
            bitrate: Audio bitrate for the output file
            
        Returns:
            Path to the converted file or None if conversion failed
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return None
            
        # Validate output format
        output_format = output_format.lower()
        if output_format not in AudioConverter.SUPPORTED_FORMATS:
            logger.error(f"Unsupported output format: {output_format}. Using mp3 instead.")
            output_format = "mp3"
            
        try:
            # Determine output file path
            if output_dir is None:
                output_dir = os.path.dirname(input_file)
            
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            filename = os.path.basename(input_file).rsplit(".", 1)[0]
            output_file = os.path.join(output_dir, f"{filename}.{output_format}")
            
            # Check if file is already in the desired format
            input_ext = os.path.splitext(input_file)[1].lower().lstrip('.')
            if input_ext == output_format:
                if input_file == output_file:
                    logger.info(f"File is already in {output_format} format: {input_file}")
                    return input_file
                else:
                    # Just copy the file
                    import shutil
                    shutil.copy2(input_file, output_file)
                    logger.info(f"Copied {output_format} file to: {output_file}")
                    return output_file
            
            # Convert to the desired format using pydub
            audio = AudioSegment.from_file(input_file)
            audio.export(output_file, format=output_format, bitrate=bitrate)
            
            logger.info(f"Successfully converted {input_file} to {output_format}: {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error converting {input_file} to {output_format}: {str(e)}")
            return None
    
    @staticmethod
    def convert_to_mp3(input_file: str, output_dir: Optional[str] = None, 
                      bitrate: str = "192k") -> Optional[str]:
        """
        Convert an audio file to MP3 format.
        
        Args:
            input_file: Path to the input audio file
            output_dir: Directory to save the output file (defaults to same as input)
            bitrate: Audio bitrate for the output file
            
        Returns:
            Path to the converted file or None if conversion failed
        """
        return AudioConverter.convert_audio(input_file, "mp3", output_dir, bitrate)
    
    @staticmethod
    def ffmpeg_convert(input_file: str, output_file: str, 
                      ffmpeg_args: Optional[list] = None) -> bool:
        """
        Use FFmpeg directly for more complex audio conversions or processing.
        
        Args:
            input_file: Path to the input audio file
            output_file: Path to the output audio file
            ffmpeg_args: Additional FFmpeg arguments
            
        Returns:
            True if conversion succeeded, False otherwise
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return False
            
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        try:
            command = ["ffmpeg", "-i", input_file]
            
            # Add any additional arguments
            if ffmpeg_args:
                command.extend(ffmpeg_args)
                
            # Add output file as the last argument
            command.append(output_file)
            
            # Run FFmpeg process
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully converted {input_file} using FFmpeg")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error during FFmpeg conversion: {str(e)}")
            return False
            
    @staticmethod
    def normalize_audio(input_file: str, output_file: Optional[str] = None, 
                       target_level: float = -18.0) -> Optional[str]:
        """
        Normalize audio levels in the file.
        
        Args:
            input_file: Path to the input audio file
            output_file: Path to the output audio file (defaults to overwrite input)
            target_level: Target audio level in dB
            
        Returns:
            Path to the normalized file or None if normalization failed
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return None
            
        try:
            # If output_file is not specified, overwrite the input file
            if output_file is None:
                output_file = input_file
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Load audio using pydub
            audio = AudioSegment.from_file(input_file)
            
            # Calculate current levels
            current_dBFS = audio.dBFS
            change_in_dBFS = target_level - current_dBFS
            
            # Apply gain to normalize
            normalized_audio = audio.apply_gain(change_in_dBFS)
            
            # Export the normalized audio
            normalized_audio.export(output_file, format=output_file.split(".")[-1])
            
            logger.info(f"Normalized audio from {current_dBFS:.2f}dB to {target_level:.2f}dB: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {str(e)}")
            return None