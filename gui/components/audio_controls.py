"""
Audio controls component for the player.
"""
import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize

class AudioControls(QWidget):
    """Audio control buttons for playback."""
    
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    previous_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Get icons directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(base_dir, "icons")
        
        # Previous button
        self.previous_button = QPushButton()
        icon_path = os.path.join(icons_dir, "skip_previous.svg")
        if os.path.exists(icon_path):
            self.previous_button.setIcon(QIcon(icon_path))
        else:
            self.previous_button.setText("Prev")
        self.previous_button.setIconSize(QSize(24, 24))
        self.previous_button.setFixedSize(40, 40)
        self.previous_button.setStyleSheet("""
            QPushButton {
                background-color: #1e2429;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #2a4055;
            }
            QPushButton:pressed {
                background-color: #3a5065;
            }
        """)
        
        # Play/Pause button
        self.play_pause_button = QPushButton()
        self.play_icon_path = os.path.join(icons_dir, "play_circle.svg")
        self.pause_icon_path = os.path.join(icons_dir, "pause_circle.svg")
        
        if os.path.exists(self.play_icon_path):
            self.play_pause_button.setIcon(QIcon(self.play_icon_path))
        else:
            self.play_pause_button.setText("Play")
            
        self.play_pause_button.setIconSize(QSize(48, 48))
        self.play_pause_button.setFixedSize(60, 60)
        self.play_pause_button.setStyleSheet("""
            QPushButton {
                background-color: #1e2429;
                border: none;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #2a4055;
            }
            QPushButton:pressed {
                background-color: #3a5065;
            }
        """)
        
        # Next button
        self.next_button = QPushButton()
        icon_path = os.path.join(icons_dir, "skip_next.svg")
        if os.path.exists(icon_path):
            self.next_button.setIcon(QIcon(icon_path))
        else:
            self.next_button.setText("Next")
        self.next_button.setIconSize(QSize(24, 24))
        self.next_button.setFixedSize(40, 40)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #1e2429;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #2a4055;
            }
            QPushButton:pressed {
                background-color: #3a5065;
            }
        """)
        
        # Add buttons to layout
        layout.addWidget(self.previous_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)
        
        # Connect signals
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.previous_button.clicked.connect(self.previous_clicked)
        self.next_button.clicked.connect(self.next_clicked)
        
    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()
            
    def set_playing(self, playing: bool):
        """Update the UI to reflect the current playing state."""
        if playing == self.is_playing:
            return
            
        self.is_playing = playing
        
        if self.is_playing:
            # We're playing, so show pause button
            if os.path.exists(self.pause_icon_path):
                self.play_pause_button.setIcon(QIcon(self.pause_icon_path))
            else:
                self.play_pause_button.setText("Pause")
        else:
            # We're paused, so show play button
            if os.path.exists(self.play_icon_path):
                self.play_pause_button.setIcon(QIcon(self.play_icon_path))
            else:
                self.play_pause_button.setText("Play")