"""
Audio controls component.
"""
import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

class AudioControls(QWidget):
    """Audio playback controls."""
    
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    previous_clicked = pyqtSignal()
    forward_30_clicked = pyqtSignal()
    back_30_clicked = pyqtSignal()
    shuffle_clicked = pyqtSignal()
    
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
        
        # Skip back 30 seconds button
        self.back_30_button = QPushButton()
        self.back_30_button.setIcon(QIcon(os.path.join(icons_dir, "replay_30.svg")))
        self.back_30_button.setIconSize(QSize(24, 24))
        self.back_30_button.setFixedSize(40, 40)
        self.back_30_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 20px;
            }
            QPushButton:pressed {
                background-color: #1a2129;
                border-radius: 20px;
            }
        """)
        self.back_30_button.clicked.connect(self.back_30_clicked.emit)
        
        # Previous button
        self.previous_button = QPushButton()
        self.previous_button.setIcon(QIcon(os.path.join(icons_dir, "skip_previous.svg")))
        self.previous_button.setIconSize(QSize(32, 32))
        self.previous_button.setFixedSize(50, 50)
        self.previous_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 25px;
            }
            QPushButton:pressed {
                background-color: #1a2129;
                border-radius: 25px;
            }
        """)
        self.previous_button.clicked.connect(self.previous_clicked.emit)
        
        # Play/Pause button
        self.play_pause_button = QPushButton()
        self.play_pause_button.setIcon(QIcon(os.path.join(icons_dir, "play_circle.svg")))
        self.play_pause_button.setIconSize(QSize(48, 48))
        self.play_pause_button.setFixedSize(60, 60)
        self.play_pause_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 30px;
            }
            QPushButton:pressed {
                background-color: #1a2129;
                border-radius: 30px;
            }
        """)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        
        # Next button
        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon(os.path.join(icons_dir, "skip_next.svg")))
        self.next_button.setIconSize(QSize(32, 32))
        self.next_button.setFixedSize(50, 50)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 25px;
            }
            QPushButton:pressed {
                background-color: #1a2129;
                border-radius: 25px;
            }
        """)
        self.next_button.clicked.connect(self.next_clicked.emit)
        
        # Skip forward 30 seconds button
        self.forward_30_button = QPushButton()
        self.forward_30_button.setIcon(QIcon(os.path.join(icons_dir, "forward_30.svg")))
        self.forward_30_button.setIconSize(QSize(24, 24))
        self.forward_30_button.setFixedSize(40, 40)
        self.forward_30_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 20px;
            }
            QPushButton:pressed {
                background-color: #1a2129;
                border-radius: 20px;
            }
        """)
        self.forward_30_button.clicked.connect(self.forward_30_clicked.emit)
        
        # Shuffle button
        self.shuffle_button = QPushButton()
        self.shuffle_button.setIcon(QIcon(os.path.join(icons_dir, "shuffle.svg")))
        self.shuffle_button.setIconSize(QSize(24, 24))
        self.shuffle_button.setFixedSize(40, 40)
        self.shuffle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 20px;
            }
            QPushButton:pressed {
                background-color: #1a2129;
                border-radius: 20px;
            }
        """)
        self.shuffle_button.clicked.connect(self.shuffle_clicked.emit)
        
        # Add buttons to layout
        layout.addWidget(self.shuffle_button)
        layout.addWidget(self.back_30_button)
        layout.addWidget(self.previous_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.forward_30_button)
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()
    
    def set_playing(self, playing):
        """Set the playing state and update button icon."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(base_dir, "icons")
        
        self.is_playing = playing
        if playing:
            self.play_pause_button.setIcon(QIcon(os.path.join(icons_dir, "pause_circle.svg")))
        else:
            self.play_pause_button.setIcon(QIcon(os.path.join(icons_dir, "play_circle.svg")))