# Audio Module

This module provides audio playback functionality with queue management and metadata handling capabilities.

## Overview

The `audio` module is designed to handle audio playback operations, including managing playback queues and processing audio metadata. It's built using PyQt5's multimedia capabilities for seamless audio integration.

## Classes and Methods

### AudioPlayer

`AudioPlayer` is a class that handles audio file playback operations.

#### Signals

- `track_started(str)`: Emitted when a track starts playing. Provides track ID.
- `track_ended()`: Emitted when a track finishes playing.
- `track_paused()`: Emitted when playback is paused.
- `track_resumed()`: Emitted when playback is resumed.
- `position_changed(int)`: Emitted when the playback position changes. Position in milliseconds.
- `duration_changed(int)`: Emitted when the track duration is determined. Duration in milliseconds.
- `volume_changed(int)`: Emitted when the volume changes. Volume as percentage (0-100).

#### Methods

- `load(file_path, track_id=None)`: Loads an audio file for playback.
  - `file_path`: Path to the audio file
  - `track_id`: Optional ID to identify the track
  - Returns: Boolean indicating success

- `play()`: Starts or resumes playback.

- `pause()`: Pauses playback.

- `stop()`: Stops playback.

- `seek(position_ms)`: Seeks to a specific position.
  - `position_ms`: Position in milliseconds

- `set_position(position_ms)`: Sets the playback position without playing.
  - `position_ms`: Position in milliseconds

- `set_position_and_play(position_ms)`: Sets the playback position and starts playing.
  - `position_ms`: Position in milliseconds

- `set_volume(volume)`: Sets the playback volume.
  - `volume`: Volume as percentage (0-100)

- `get_position()`: Gets the current position in milliseconds.
  - Returns: Current position in milliseconds

- `get_duration()`: Gets the total duration in milliseconds.
  - Returns: Total duration in milliseconds

- `is_playing()`: Checks if the player is currently playing.
  - Returns: Boolean indicating if playback is active

### QueueManager

The `QueueManager` class is provided for managing playback queues and history.

**Note**: The implementation details of this class are not fully provided in the shared files.

### Metadata Module

A metadata handling module is provided for reading and writing audio file metadata.

**Note**: The implementation details of this module are not fully provided in the shared files.