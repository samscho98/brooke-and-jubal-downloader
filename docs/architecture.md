# YouTube Playlist Downloader - Architecture

## Overview

The YouTube Playlist Downloader application is structured as a modular, multi-layered system with clear separation of concerns. This document outlines the high-level architecture and key components.

## Core Components

### 1. Downloader Module

Responsible for interacting with YouTube and downloading content.

- `youtube.py` - Interacts with YouTube API/yt-dlp
- `converter.py` - Handles audio format conversion
- `tracker.py` - Tracks download history

### 2. Scoring Module

Implements algorithms for scoring and queue management.

- `score_calculator.py` - Core scoring algorithms
- `queue_manager.py` - Generates play queues
- `metrics_tracker.py` - Tracks playback performance

### 3. Data Module

Handles data persistence and configuration.

- `storage.py` - Abstract storage interface
- `json_storage.py` - JSON implementation
- `file_manager.py` - File system operations
- `config_manager.py` - Configuration management

### 4. GUI Module

Provides the user interface.

- `sidebar_app.py` - Main application window
- Views - Content views for sidebar sections
- Components - Reusable UI elements

### 5. Audio Module

Handles audio playback and queue management.

- `player.py` - Audio playback functionality
- `queue_manager.py` - Manages playback queues

## Data Flow

1. User requests playlist download via GUI/CLI
2. Downloader fetches videos and metadata
3. Downloaded files are organized by FileManager
4. Scoring system calculates scores for content
5. Audio player uses scores to create optimal queues

## Design Patterns

- **Repository Pattern** - For data access abstraction
- **Observer Pattern** - For event communication
- **Strategy Pattern** - For scoring algorithms
- **Factory Pattern** - For UI components

## Configuration

All settings are stored in `config.ini` with these main sections:

- `[general]` - General application settings
- `[audio]` - Audio conversion settings
- `[player]` - Playback settings
- `[scoring]` - Scoring algorithm settings
- `[logging]` - Logging configuration
