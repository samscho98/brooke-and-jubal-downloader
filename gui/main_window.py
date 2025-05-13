"""
Updated main_window.py with proper initialization of PlayerPage
"""
import os
import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QStackedLayout, QLabel, QFrame, QLineEdit, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QSlider, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Import backend components
from data.config_manager import ConfigHandler
from downloader.youtube import YouTubeDownloader
from downloader.tracker import DownloadTracker
from downloader.scoring import ScoringSystem

# Import GUI pages
from gui.pages.player_page import PlayerPage
from gui.pages.playlists_page import PlaylistsPage
from gui.pages.analytics_page import AnalyticsPage
from gui.pages.settings_page import SettingsPage
from gui.pages.about_page import AboutPage

from utils.path_utils import get_audio_path, get_data_path, get_path

# Import audio components
from audio.player import AudioPlayer

# Import PyQt stylesheet
import qdarkstyle

class YouTubePlaylistDownloaderApp(QWidget):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Playlist Downloader")
        self.setMinimumSize(1100, 700)
        
        # Initialize backend components
        self.config = ConfigHandler(get_path("config.ini"))
        self.output_dir = self.config.get("general", "output_directory", get_data_path("audio"))

        # Create tracker before downloader
        self.tracker = DownloadTracker(
            history_file=get_data_path("download_history.json"),
            playlists_file=get_data_path("playlists.json")
        )

        # Pass tracker to downloader
        self.downloader = YouTubeDownloader(self.output_dir, self.config, self.tracker)

        # Initialize scoring system with correct path
        self.scoring = ScoringSystem(get_data_path("video_scores.json"))

        # Initialize audio player
        self.audio_player = AudioPlayer()
        
        # Initialize UI
        self.init_ui()
        
        # Set initial page
        self.change_page("Audio Player")
    
    def init_ui(self):
        """Initialize the user interface."""
        font = QFont()
        font.setPointSize(12)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Side menu
        side_menu_frame = QFrame()
        side_menu_frame.setObjectName("sidebar")
        side_menu_frame.setStyleSheet("""
            #sidebar {
                background-color: #1e2429;
                border-right: 1px solid #121920;
            }
        """)
        side_menu_frame.setFixedWidth(180)
        side_menu_layout = QVBoxLayout(side_menu_frame)
        side_menu_layout.setContentsMargins(10, 20, 10, 20)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        
        logo_path = os.path.join("gui", "icons", "logo.svg")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback text logo
            logo_label.setText("YT Downloader")
            logo_label.setFont(QFont("Arial", 14, QFont.Bold))
            logo_label.setStyleSheet("color: #ffffff;")
            
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        side_menu_layout.addLayout(logo_layout)
        side_menu_layout.addSpacing(20)
        
        # Menu buttons
        self.menu_buttons = []
        button_infos = [
            ("Audio Player", "play_circle.svg"),
            ("Playlists", "playlist_add.svg"),
            ("Analytics", "analytics.svg"),
            ("Settings", "settings.svg"),
            ("About", "info.svg")
        ]
        
        for name, icon_name in button_infos:
            btn = QPushButton(name)
            btn.setFont(font)
            btn.setMinimumHeight(50)
            
            # Set icon if available
            icon_path = os.path.join("gui", "icons", icon_name)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(24, 24))
            
            btn.setObjectName("sidebar_button")
            btn.setStyleSheet("""
                #sidebar_button {
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                    border-radius: 5px;
                    background-color: transparent;
                }
                #sidebar_button:hover {
                    background-color: #273341;
                }
                #sidebar_button:checked {
                    background-color: #2a4055;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=name: self.change_page(name))
            side_menu_layout.addWidget(btn)
            self.menu_buttons.append((name, btn))
        
        side_menu_layout.addStretch()
        
        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("content")
        content_frame.setStyleSheet("""
            #content {
                background-color: #121920;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Stacked layout for pages
        self.stacked_layout = QStackedLayout()
        
        # Create pages
        self.player_page = PlayerPage(
            self.tracker, 
            self.scoring, 
            self.audio_player,
            self.downloader  # Pass the downloader instance
        )
        self.playlists_page = PlaylistsPage(self.downloader, self.tracker)
        self.analytics_page = AnalyticsPage()  # Use placeholder version with no parameters
        self.settings_page = SettingsPage(self.config, self.downloader)
        self.about_page = AboutPage()
        
        # Add pages to stacked layout
        self.stacked_layout.addWidget(self.player_page)
        self.stacked_layout.addWidget(self.playlists_page)
        self.stacked_layout.addWidget(self.analytics_page)
        self.stacked_layout.addWidget(self.settings_page)
        self.stacked_layout.addWidget(self.about_page)
        
        content_layout.addLayout(self.stacked_layout)
        
        # Add components to main layout
        main_layout.addWidget(side_menu_frame)
        main_layout.addWidget(content_frame, 1)
        
        # Connect signals
        self.playlists_page.playlist_updated.connect(self.player_page.refresh_queue)
    
    def change_page(self, page_name):
        """Change the current page."""
        page_indices = {
            "Audio Player": 0,
            "Playlists": 1,
            "Analytics": 2,
            "Settings": 3,
            "About": 4
        }
        
        # Set the current page
        index = page_indices.get(page_name, 0)
        self.stacked_layout.setCurrentIndex(index)
        
        # Update button states
        for name, btn in self.menu_buttons:
            btn.setChecked(name == page_name)
        
        # Set window title
        self.setWindowTitle(f"YouTube Playlist Downloader - {page_name}")
        logging.info(f"Changed to page: {page_name}")