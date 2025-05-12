"""
About page for the YouTube Playlist Downloader.
"""
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices, QPixmap

class AboutPage(QWidget):
    """About and information page."""
    
    def __init__(self):
        """Initialize about page."""
        super().__init__()
        
        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # App logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        
        try:
            logo_path = os.path.join("gui", "icons", "logo.svg")
            if os.path.exists(logo_path):
                logo_pixmap = QPixmap(logo_path)
                logo_label.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                # Fallback text logo
                logo_label.setText("YouTube Playlist\nDownloader")
                logo_label.setFont(QFont("Arial", 20, QFont.Bold))
                logo_label.setStyleSheet("color: #2a82da;")
        except:
            # Fallback text logo
            logo_label.setText("YouTube Playlist\nDownloader")
            logo_label.setFont(QFont("Arial", 20, QFont.Bold))
            logo_label.setStyleSheet("color: #2a82da;")
            
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        # App info
        title_label = QLabel("YouTube Playlist Downloader")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        # Try to get version
        try:
            from version import __version__
            version_str = __version__
        except:
            version_str = "1.0.0"
            
        version_label = QLabel(f"Version {version_str}")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)
        
        # Description
        description = (
            "YouTube Playlist Downloader is an application that downloads videos from YouTube playlists "
            "as audio files and keeps track of downloaded files to ensure your collection stays up to date. "
            "It includes an audio player with intelligent queue management based on scoring algorithms."
        )
        description_label = QLabel(description)
        description_label.setFont(QFont("Arial", 11))
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        
        # Features
        features_title = QLabel("Key Features")
        features_title.setFont(QFont("Arial", 14, QFont.Bold))
        features_title.setAlignment(Qt.AlignCenter)
        
        features = (
            "• Download videos and playlists as audio files\n"
            "• Track playlists to keep your collection up-to-date\n"
            "• Play audio files with integrated player\n"
            "• Intelligent queue management with scoring system\n"
            "• Clean, modern user interface\n"
            "• Command-line interface for automation"
        )
        
        features_label = QLabel(features)
        features_label.setFont(QFont("Arial", 11))
        features_label.setAlignment(Qt.AlignLeft)
        
        # Legal disclaimer
        disclaimer_title = QLabel("Legal Disclaimer")
        disclaimer_title.setFont(QFont("Arial", 14, QFont.Bold))
        disclaimer_title.setAlignment(Qt.AlignCenter)
        
        disclaimer = (
            "This software is provided for educational and personal use only. The developer(s) of this application:"
            "\n\n"
            "• Do not endorse or encourage the unauthorized downloading of copyrighted content\n"
            "• Are not responsible for how users choose to use this software\n"
            "• Accept no liability for misuse of this software or any consequences thereof\n"
            "• Make no guarantees regarding the legality of downloading specific content\n"
            "\n"
            "Users are solely responsible for ensuring they have the right to download any content "
            "and for complying with YouTube's Terms of Service."
        )
        disclaimer_label = QLabel(disclaimer)
        disclaimer_label.setFont(QFont("Arial", 10))
        disclaimer_label.setWordWrap(True)
        disclaimer_label.setAlignment(Qt.AlignLeft)
        
        # Frame for disclaimer
        disclaimer_frame = QWidget()
        disclaimer_frame.setObjectName("disclaimer_frame")
        disclaimer_frame.setStyleSheet("""
            #disclaimer_frame {
                background-color: #1a2129;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        disclaimer_layout = QVBoxLayout(disclaimer_frame)
        disclaimer_layout.addWidget(disclaimer_title)
        disclaimer_layout.addWidget(disclaimer_label)
        
        # Links
        links_layout = QHBoxLayout()
        
        github_button = QPushButton("GitHub Repository")
        github_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3a92ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        github_button.clicked.connect(self.open_github)
        
        license_button = QPushButton("View License")
        license_button.setStyleSheet("""
            QPushButton {
                background-color: #2a4055;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3a5065;
            }
            QPushButton:pressed {
                background-color: #1a3045;
            }
        """)
        license_button.clicked.connect(self.show_license)
        
        links_layout.addStretch()
        links_layout.addWidget(github_button)
        links_layout.addSpacing(10)
        links_layout.addWidget(license_button)
        links_layout.addStretch()
        
        # Assemble layout
        layout.addLayout(logo_layout)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addSpacing(20)
        layout.addWidget(description_label)
        layout.addSpacing(20)
        layout.addWidget(features_title)
        layout.addWidget(features_label)
        layout.addSpacing(20)
        layout.addWidget(disclaimer_frame)
        layout.addSpacing(20)
        layout.addLayout(links_layout)
        layout.addStretch()

    def open_github(self):
        """Open the GitHub repository in browser."""
        QDesktopServices.openUrl(QUrl("https://github.com/samscho98/youtube-playlist-downloader"))

    def show_license(self):
        """Show license information."""
        license_text = """
MIT License

Copyright (c) 2025 YouTube Playlist Downloader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
        """
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "License", license_text)