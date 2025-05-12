"""
Audio metadata module.
Handles reading and writing audio file metadata.
"""
import os
import logging
from typing import Dict, Optional, Any

try:
    import mutagen
    from mutagen.id3 import ID3, TIT2, TALB, TPE1, TDRC, COMM, TCON
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    MUTAGEN_AVAILABLE = True
except ImportError:
    logging.warning("Mutagen library not available. Metadata functions will be limited.")
    MUTAGEN_AVAILABLE = False

class MetadataHandler:
    """Handles audio file metadata operations."""
    
    # Supported file extensions
    SUPPORTED_FORMATS = {
        'mp3': 'mp3',
        'm4a': 'mp4',
        'mp4': 'mp4',
        'flac': 'flac',
        'ogg': 'ogg',
        'opus': 'opus',
        'wav': 'wav'
    }
    
    @staticmethod
    def read_metadata(file_path: str) -> Dict[str, Any]:
        """
        Read metadata from an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary of metadata values
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return {}
            
        if not MUTAGEN_AVAILABLE:
            logging.warning("Mutagen not available, returning basic file info only")
            return MetadataHandler._get_basic_info(file_path)
            
        try:
            # Determine file type by extension
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            file_type = MetadataHandler.SUPPORTED_FORMATS.get(ext)
            
            if not file_type:
                logging.warning(f"Unsupported file type: {ext}")
                return MetadataHandler._get_basic_info(file_path)
                
            # Read metadata based on file type
            if file_type == 'mp3':
                return MetadataHandler._read_mp3_metadata(file_path)
            elif file_type == 'mp4':
                return MetadataHandler._read_mp4_metadata(file_path)
            elif file_type == 'flac':
                return MetadataHandler._read_flac_metadata(file_path)
            elif file_type in ['ogg', 'opus']:
                return MetadataHandler._read_ogg_metadata(file_path)
            else:
                # Try generic mutagen approach
                audio = mutagen.File(file_path)
                if audio:
                    metadata = MetadataHandler._get_basic_info(file_path)
                    metadata.update(MetadataHandler._extract_common_metadata(audio))
                    return metadata
                    
                return MetadataHandler._get_basic_info(file_path)
                
        except Exception as e:
            logging.error(f"Error reading metadata: {str(e)}")
            return MetadataHandler._get_basic_info(file_path)
    
    @staticmethod
    def write_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to an audio file.
        
        Args:
            file_path: Path to the audio file
            metadata: Dictionary of metadata values to write
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return False
            
        if not MUTAGEN_AVAILABLE:
            logging.error("Mutagen not available, cannot write metadata")
            return False
            
        try:
            # Determine file type by extension
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            file_type = MetadataHandler.SUPPORTED_FORMATS.get(ext)
            
            if not file_type:
                logging.warning(f"Unsupported file type: {ext}")
                return False
                
            # Write metadata based on file type
            if file_type == 'mp3':
                return MetadataHandler._write_mp3_metadata(file_path, metadata)
            elif file_type == 'mp4':
                return MetadataHandler._write_mp4_metadata(file_path, metadata)
            elif file_type == 'flac':
                return MetadataHandler._write_flac_metadata(file_path, metadata)
            elif file_type in ['ogg', 'opus']:
                return MetadataHandler._write_ogg_metadata(file_path, metadata)
            else:
                # Try generic mutagen approach
                audio = mutagen.File(file_path)
                if audio:
                    for key, value in metadata.items():
                        if key in audio and value:
                            audio[key] = value
                    audio.save()
                    return True
                    
                return False
                
        except Exception as e:
            logging.error(f"Error writing metadata: {str(e)}")
            return False
    
    @staticmethod
    def _get_basic_info(file_path: str) -> Dict[str, Any]:
        """
        Get basic file information as fallback.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary of basic file information
        """
        try:
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Try to extract artist and title from filename (Artist - Title format)
            parts = name_without_ext.split(' - ', 1)
            
            info = {
                'filename': filename,
                'filesize': os.path.getsize(file_path),
                'modified': os.path.getmtime(file_path),
                'path': file_path
            }
            
            if len(parts) > 1:
                info['artist'] = parts[0].strip()
                info['title'] = parts[1].strip()
            else:
                info['title'] = name_without_ext
                
            return info
            
        except Exception as e:
            logging.error(f"Error getting basic file info: {str(e)}")
            return {'filename': os.path.basename(file_path), 'path': file_path}
    
    @staticmethod
    def _extract_common_metadata(audio: Any) -> Dict[str, Any]:
        """
        Extract common metadata from a mutagen object.
        
        Args:
            audio: Mutagen audio object
            
        Returns:
            Dictionary of common metadata
        """
        metadata = {}
        
        # Try to extract duration
        if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
            metadata['duration'] = audio.info.length
            
        # Try to extract bitrate
        if hasattr(audio, 'info') and hasattr(audio.info, 'bitrate'):
            metadata['bitrate'] = audio.info.bitrate
            
        # Try to extract common tags
        for tag, variants in {
            'title': ['title', 'TITLE', 'TIT2'],
            'artist': ['artist', 'ARTIST', 'TPE1', 'performer'],
            'album': ['album', 'ALBUM', 'TALB'],
            'date': ['date', 'DATE', 'TDRC', 'year'],
            'genre': ['genre', 'GENRE', 'TCON'],
            'comment': ['comment', 'COMMENT', 'COMM'],
            'track': ['track', 'TRACK', 'tracknumber'],
        }.items():
            for variant in variants:
                if variant in audio:
                    value = audio[variant]
                    if isinstance(value, list):
                        value = value[0]
                    if hasattr(value, 'text'):
                        value = value.text
                    metadata[tag] = str(value)
                    break
                    
        return metadata
    
    @staticmethod
    def _read_mp3_metadata(file_path: str) -> Dict[str, Any]:
        """
        Read metadata from an MP3 file.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            Dictionary of metadata values
        """
        try:
            audio = MP3(file_path)
            metadata = MetadataHandler._get_basic_info(file_path)
            
            # Add audio properties
            if hasattr(audio, 'info'):
                metadata['duration'] = audio.info.length
                metadata['bitrate'] = audio.info.bitrate
                metadata['sample_rate'] = audio.info.sample_rate
                metadata['channels'] = audio.info.channels
                
            # Try to load ID3 tags
            try:
                tags = ID3(file_path)
                
                # Extract common tags
                if 'TIT2' in tags:
                    metadata['title'] = str(tags['TIT2'])
                if 'TPE1' in tags:
                    metadata['artist'] = str(tags['TPE1'])
                if 'TALB' in tags:
                    metadata['album'] = str(tags['TALB'])
                if 'TDRC' in tags:
                    metadata['date'] = str(tags['TDRC'])
                if 'TCON' in tags:
                    metadata['genre'] = str(tags['TCON'])
                if 'COMM' in tags:
                    metadata['comment'] = str(tags['COMM'])
                if 'TRCK' in tags:
                    metadata['track'] = str(tags['TRCK'])
            except:
                # ID3 tags might not be present
                pass
                
            return metadata
            
        except Exception as e:
            logging.error(f"Error reading MP3 metadata: {str(e)}")
            return MetadataHandler._get_basic_info(file_path)
    
    @staticmethod
    def _read_mp4_metadata(file_path: str) -> Dict[str, Any]:
        """
        Read metadata from an MP4/M4A file.
        
        Args:
            file_path: Path to the MP4/M4A file
            
        Returns:
            Dictionary of metadata values
        """
        try:
            audio = MP4(file_path)
            metadata = MetadataHandler._get_basic_info(file_path)
            
            # Add audio properties
            if hasattr(audio, 'info'):
                metadata['duration'] = audio.info.length
                metadata['bitrate'] = audio.info.bitrate
                metadata['sample_rate'] = audio.info.sample_rate
                metadata['channels'] = audio.info.channels
                
            # MP4 tag mapping
            tag_mapping = {
                '©nam': 'title',
                '©ART': 'artist',
                '©alb': 'album',
                '©day': 'date',
                '©gen': 'genre',
                '©cmt': 'comment',
                'trkn': 'track'
            }
            
            # Extract tags
            for mp4_tag, metadata_tag in tag_mapping.items():
                if mp4_tag in audio:
                    value = audio[mp4_tag]
                    if isinstance(value, list):
                        if isinstance(value[0], tuple):
                            # Handle track number which is a tuple
                            metadata[metadata_tag] = str(value[0][0])
                        else:
                            metadata[metadata_tag] = str(value[0])
                            
            return metadata
            
        except Exception as e:
            logging.error(f"Error reading MP4 metadata: {str(e)}")
            return MetadataHandler._get_basic_info(file_path)
    
    @staticmethod
    def _read_flac_metadata(file_path: str) -> Dict[str, Any]:
        """
        Read metadata from a FLAC file.
        
        Args:
            file_path: Path to the FLAC file
            
        Returns:
            Dictionary of metadata values
        """
        try:
            audio = FLAC(file_path)
            metadata = MetadataHandler._get_basic_info(file_path)
            
            # Add audio properties
            if hasattr(audio, 'info'):
                metadata['duration'] = audio.info.length
                metadata['bitrate'] = audio.info.bitrate
                metadata['sample_rate'] = audio.info.sample_rate
                metadata['channels'] = audio.info.channels
                metadata['bits_per_sample'] = audio.info.bits_per_sample
                
            # FLAC tag mapping (case insensitive)
            tag_mapping = {
                'title': 'title',
                'artist': 'artist',
                'album': 'album',
                'date': 'date',
                'genre': 'genre',
                'comment': 'comment',
                'tracknumber': 'track'
            }
            
            # Extract tags
            for flac_tag, metadata_tag in tag_mapping.items():
                if flac_tag in audio:
                    value = audio[flac_tag]
                    if isinstance(value, list) and value:
                        metadata[metadata_tag] = str(value[0])
                        
            return metadata
            
        except Exception as e:
            logging.error(f"Error reading FLAC metadata: {str(e)}")
            return MetadataHandler._get_basic_info(file_path)
    
    @staticmethod
    def _read_ogg_metadata(file_path: str) -> Dict[str, Any]:
        """
        Read metadata from an OGG file.
        
        Args:
            file_path: Path to the OGG file
            
        Returns:
            Dictionary of metadata values
        """
        try:
            audio = OggVorbis(file_path)
            metadata = MetadataHandler._get_basic_info(file_path)
            
            # Add audio properties
            if hasattr(audio, 'info'):
                metadata['duration'] = audio.info.length
                metadata['bitrate'] = audio.info.bitrate
                metadata['sample_rate'] = audio.info.sample_rate
                metadata['channels'] = audio.info.channels
                
            # OGG tag mapping (case insensitive)
            tag_mapping = {
                'title': 'title',
                'artist': 'artist',
                'album': 'album',
                'date': 'date',
                'genre': 'genre',
                'comment': 'comment',
                'tracknumber': 'track'
            }
            
            # Extract tags
            for ogg_tag, metadata_tag in tag_mapping.items():
                if ogg_tag in audio:
                    value = audio[ogg_tag]
                    if isinstance(value, list) and value:
                        metadata[metadata_tag] = str(value[0])
                        
            return metadata
            
        except Exception as e:
            logging.error(f"Error reading OGG metadata: {str(e)}")
            return MetadataHandler._get_basic_info(file_path)
    
    @staticmethod
    def _write_mp3_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to an MP3 file.
        
        Args:
            file_path: Path to the MP3 file
            metadata: Dictionary of metadata values to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to load existing ID3 tags or create new
            try:
                tags = ID3(file_path)
            except:
                tags = ID3()
                
            # Update tags
            if 'title' in metadata:
                tags['TIT2'] = TIT2(encoding=3, text=metadata['title'])
            if 'artist' in metadata:
                tags['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
            if 'album' in metadata:
                tags['TALB'] = TALB(encoding=3, text=metadata['album'])
            if 'date' in metadata:
                tags['TDRC'] = TDRC(encoding=3, text=metadata['date'])
            if 'genre' in metadata:
                tags['TCON'] = TCON(encoding=3, text=metadata['genre'])
            if 'comment' in metadata:
                tags['COMM'] = COMM(encoding=3, lang='eng', desc='', text=metadata['comment'])
                
            # Save tags
            tags.save(file_path)
            return True
            
        except Exception as e:
            logging.error(f"Error writing MP3 metadata: {str(e)}")
            return False
    
    @staticmethod
    def _write_mp4_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to an MP4/M4A file.
        
        Args:
            file_path: Path to the MP4/M4A file
            metadata: Dictionary of metadata values to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audio = MP4(file_path)
            
            # MP4 tag mapping
            tag_mapping = {
                'title': '©nam',
                'artist': '©ART',
                'album': '©alb',
                'date': '©day',
                'genre': '©gen',
                'comment': '©cmt'
            }
            
            # Update tags
            for metadata_tag, mp4_tag in tag_mapping.items():
                if metadata_tag in metadata:
                    audio[mp4_tag] = [metadata[metadata_tag]]
                    
            # Track number requires special handling
            if 'track' in metadata:
                try:
                    track_num = int(metadata['track'].split('/')[0])
                    if 'trkn' in audio:
                        total_tracks = audio['trkn'][0][1]
                        audio['trkn'] = [(track_num, total_tracks)]
                    else:
                        audio['trkn'] = [(track_num, 0)]
                except:
                    pass
                    
            # Save tags
            audio.save()
            return True
            
        except Exception as e:
            logging.error(f"Error writing MP4 metadata: {str(e)}")
            return False
    
    @staticmethod
    def _write_flac_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to a FLAC file.
        
        Args:
            file_path: Path to the FLAC file
            metadata: Dictionary of metadata values to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audio = FLAC(file_path)
            
            # FLAC tag mapping
            tag_mapping = {
                'title': 'TITLE',
                'artist': 'ARTIST',
                'album': 'ALBUM',
                'date': 'DATE',
                'genre': 'GENRE',
                'comment': 'COMMENT',
                'track': 'TRACKNUMBER'
            }
            
            # Update tags
            for metadata_tag, flac_tag in tag_mapping.items():
                if metadata_tag in metadata:
                    audio[flac_tag] = metadata[metadata_tag]
                    
            # Save tags
            audio.save()
            return True
            
        except Exception as e:
            logging.error(f"Error writing FLAC metadata: {str(e)}")
            return False
    
    @staticmethod
    def _write_ogg_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to an OGG file.
        
        Args:
            file_path: Path to the OGG file
            metadata: Dictionary of metadata values to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audio = OggVorbis(file_path)
            
            # OGG tag mapping
            tag_mapping = {
                'title': 'title',
                'artist': 'artist',
                'album': 'album',
                'date': 'date',
                'genre': 'genre',
                'comment': 'comment',
                'track': 'tracknumber'
            }
            
            # Update tags
            for metadata_tag, ogg_tag in tag_mapping.items():
                if metadata_tag in metadata:
                    audio[ogg_tag] = metadata[metadata_tag]
                    
            # Save tags
            audio.save()
            return True
            
        except Exception as e:
            logging.error(f"Error writing OGG metadata: {str(e)}")
            return False