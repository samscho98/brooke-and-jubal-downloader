"""
Volume control component.
"""
import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

class VolumeControl(QWidget):
    """Volume control slider with label."""
    
    volume_changed = pyqtSignal(int)  # Volume as percentage (0-100)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Get icons directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(base_dir, "icons")
        
        # Volume icon button
        self.volume_icon = QPushButton()
        self.volume_icon.setIcon(QIcon(os.path.join(icons_dir, "volume_up.svg")))
        self.volume_icon.setIconSize(QSize(24, 24))
        self.volume_icon.setFixedSize(32, 32)
        self.volume_icon.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #273341;
                border-radius: 16px;
            }
        """)
        self.volume_icon.clicked.connect(self.toggle_mute)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setFixedWidth(120)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #2a2a2a;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #cc3300;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #cc3300;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        # Volume label
        self.volume_label = QLabel("80%")
        self.volume_label.setStyleSheet("color: #cccccc;")
        self.volume_label.setFixedWidth(40)
        
        # Add widgets to layout
        layout.addWidget(self.volume_icon)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.volume_label)
        
        # Store the previous volume before muting
        self.previous_volume = 80
        self.is_muted = False
        
    def on_volume_changed(self, value):
        """Handle volume slider change."""
        self.volume_label.setText(f"{value}%")
        self.volume_changed.emit(value)
        
        # Update mute state and icon
        if value == 0:
            self.is_muted = True
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "volume_off.svg")
            self.volume_icon.setIcon(QIcon(icon_path))
        else:
            self.is_muted = False
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "volume_up.svg")
            self.volume_icon.setIcon(QIcon(icon_path))
            self.previous_volume = value
    
    def toggle_mute(self):
        """Toggle between muted and unmuted states."""
        if self.is_muted:
            # Unmute
            self.volume_slider.setValue(self.previous_volume)
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "volume_up.svg")
            self.volume_icon.setIcon(QIcon(icon_path))
            self.is_muted = False
        else:
            # Mute
            self.previous_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "volume_off.svg")
            self.volume_icon.setIcon(QIcon(icon_path))
            self.is_muted = True
    
    def set_volume(self, volume):
        """Set the volume directly."""
        self.volume_slider.setValue(volume)