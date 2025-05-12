#!/usr/bin/env python3
"""
Setup script for YouTube Playlist Downloader.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read version from version.py
with open("version.py") as f:
    version_info = {}
    exec(f.read(), version_info)
    version = version_info["__version__"]

# Read long description from README.md
long_description = Path("README.md").read_text()

setup(
    name="youtube-playlist-downloader",
    version=version,
    description="Download and manage YouTube playlists as audio files, for playing as TikTok Live background music.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sam Schonenberg",
    author_email="sam.schonenberg@gmail.com",
    url="https://github.com/samscho98/youtube-playlist-downloader",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2023.10.0",
        "pydub>=0.25.1",
        "requests>=2.31.0",
        "Pillow>=10.0.0",
        "rich>=13.5.0",
        "typer>=0.9.0",
        "ffmpeg-python>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "yt-playlist-dl=main:main",
            "yt-playlist-dl-cli=cli_main:main",
            "yt-playlist-dl-gui=gui_main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Internet",
    ],
    python_requires=">=3.8",
)
