"""Analytics page for the YouTube Playlist Downloader."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class AnalyticsPage(QWidget):
    """
    Placeholder Analytics and statistics page.
    
    Note: This is a simplified placeholder that doesn't rely on the tracker or scoring system.
    The full implementation with statistics, charts, and metrics will be added later.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create a simple placeholder message
        title_label = QLabel("Analytics Page")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        
        description_label = QLabel(
            "This is a placeholder for the analytics page. "
            "The full analytics functionality will be implemented in a future update.\n\n"
            "Future features will include:\n"
            "• Playback statistics and history\n"
            "• Most listened tracks and playlists\n"
            "• Advanced scoring visualization\n"
            "• Usage patterns and recommendations"
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 14px;")
        
        # Add a refresh button for future use
        refresh_button = QPushButton("Refresh Analytics")
        refresh_button.setFixedWidth(200)
        refresh_button.setEnabled(False)  # Disabled for now
        
        # Add coming soon notice
        coming_soon = QLabel("Full analytics implementation coming soon...")
        coming_soon.setAlignment(Qt.AlignCenter)
        coming_soon.setStyleSheet("font-style: italic; color: #888;")
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(refresh_button, 0, Qt.AlignCenter)
        layout.addWidget(coming_soon)
        layout.addStretch()