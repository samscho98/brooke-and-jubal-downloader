"""
Audio progress slider component.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

class TimeSlider(QWidget):
    """Time slider with position labels."""
    
    position_changed = pyqtSignal(int)  # Position in milliseconds
    slider_pressed = pyqtSignal()
    slider_released = pyqtSignal(int)  # Position in milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration = 0
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumHeight(20)
        self.slider.setRange(0, 1000)  # We'll convert to milliseconds
        self.slider.setValue(0)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #2a2a2a;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #2a82da;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #2a82da;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        
        # Connect signals
        self.slider.sliderMoved.connect(self.on_slider_moved)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        
        # Time labels
        labels_layout = QHBoxLayout()
        labels_layout.setContentsMargins(0, 0, 0, 0)
        
        self.current_position_label = QLabel("0:00")
        self.current_position_label.setStyleSheet("color: #cccccc;")
        
        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("color: #cccccc;")
        
        labels_layout.addWidget(self.current_position_label)
        labels_layout.addStretch()
        labels_layout.addWidget(self.duration_label)
        
        # Add to main layout
        main_layout.addWidget(self.slider)
        main_layout.addLayout(labels_layout)
    
    def set_duration(self, duration_ms):
        """Set the audio duration in milliseconds."""
        self.duration = duration_ms
        self.update_duration_label()
    
    def update_position(self, position_ms):
        """Update the current position in milliseconds."""
        if self.duration > 0 and not self.slider.isSliderDown():
            # Calculate position percentage (0 to 1000)
            position_value = int((position_ms / self.duration) * 1000)
            self.slider.setValue(position_value)
            
            # Update label
            self.update_position_label(position_ms)
    
    def on_slider_moved(self, value):
        """Handle slider value change."""
        if self.duration > 0:
            # Convert slider value to milliseconds
            position_ms = int((value / 1000) * self.duration)
            self.update_position_label(position_ms)
            self.position_changed.emit(position_ms)
    
    def on_slider_pressed(self):
        """Handle slider press."""
        self.slider_pressed.emit()
    
    def on_slider_released(self):
        """Handle slider release."""
        if self.duration > 0:
            # Convert slider value to milliseconds
            value = self.slider.value()
            position_ms = int((value / 1000) * self.duration)
            self.slider_released.emit(position_ms)
    
    def update_position_label(self, position_ms):
        """Update the position label with the current time."""
        seconds = position_ms // 1000
        minutes = seconds // 60
        seconds %= 60
        self.current_position_label.setText(f"{minutes}:{seconds:02d}")
    
    def update_duration_label(self):
        """Update the duration label with the total time."""
        seconds = self.duration // 1000
        minutes = seconds // 60
        seconds %= 60
        self.duration_label.setText(f"{minutes}:{seconds:02d}")