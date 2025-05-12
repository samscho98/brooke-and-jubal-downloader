"""
Dialog for creating and managing playback queues.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QPushButton, QCheckBox, QSpinBox, QGroupBox, QFormLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

class QueueDialog(QDialog):
    """Dialog for creating and customizing playback queues."""
    
    queue_created = pyqtSignal(dict)  # Queue parameters
    
    def __init__(self, parent=None):
        """
        Initialize the queue dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Create Queue")
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Queue type selection
        queue_type_group = QGroupBox("Queue Type")
        queue_type_layout = QFormLayout(queue_type_group)
        
        self.queue_type_combo = QComboBox()
        self.queue_type_combo.addItems(["Smart Queue", "Playlist Queue", "Custom Queue"])
        self.queue_type_combo.currentIndexChanged.connect(self.on_queue_type_changed)
        queue_type_layout.addRow("Type:", self.queue_type_combo)
        
        # Additional selection for playlist
        self.playlist_combo = QComboBox()
        self.playlist_combo.setEnabled(False)
        queue_type_layout.addRow("Playlist:", self.playlist_combo)
        
        layout.addWidget(queue_type_group)
        
        # Queue options
        options_group = QGroupBox("Queue Options")
        options_layout = QFormLayout(options_group)
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 100)
        self.limit_spin.setValue(25)
        self.limit_spin.setSuffix(" tracks")
        options_layout.addRow("Limit:", self.limit_spin)
        
        self.shuffle_check = QCheckBox("Enable shuffle")
        self.shuffle_check.setChecked(True)
        options_layout.addRow("", self.shuffle_check)
        
        self.include_history_check = QCheckBox("Include recently played")
        self.include_history_check.setChecked(False)
        options_layout.addRow("", self.include_history_check)
        
        layout.addWidget(options_group)
        
        # Smart queue options
        self.smart_options_group = QGroupBox("Smart Queue Options")
        smart_options_layout = QFormLayout(self.smart_options_group)
        
        self.time_weight_spin = QSpinBox()
        self.time_weight_spin.setRange(0, 100)
        self.time_weight_spin.setValue(50)
        self.time_weight_spin.setSuffix("%")
        smart_options_layout.addRow("Time-of-day Weight:", self.time_weight_spin)
        
        self.popularity_weight_spin = QSpinBox()
        self.popularity_weight_spin.setRange(0, 100)
        self.popularity_weight_spin.setValue(30)
        self.popularity_weight_spin.setSuffix("%")
        smart_options_layout.addRow("Popularity Weight:", self.popularity_weight_spin)
        
        self.freshness_weight_spin = QSpinBox()
        self.freshness_weight_spin.setRange(0, 100)
        self.freshness_weight_spin.setValue(20)
        self.freshness_weight_spin.setSuffix("%")
        smart_options_layout.addRow("Freshness Weight:", self.freshness_weight_spin)
        
        layout.addWidget(self.smart_options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.create_button = QPushButton("Create Queue")
        self.create_button.clicked.connect(self.create_queue)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
        
        # Populate playlists
        self.populate_playlists()
        
    def populate_playlists(self):
        """Populate the playlists combobox."""
        self.playlist_combo.clear()
        
        # Try to get playlists from parent window
        try:
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'tracker'):
                main_window = main_window.parent()
                
            if main_window and hasattr(main_window, 'tracker'):
                playlists = main_window.tracker.get_playlists()
                
                # Add playlists to combo
                for playlist in playlists:
                    name = playlist.get("name", "Unknown")
                    self.playlist_combo.addItem(name, playlist.get("url", ""))
                
                # Add "Other" for single videos
                self.playlist_combo.addItem("Other", "other_videos")
            else:
                # Default playlists if we can't get real ones
                self.playlist_combo.addItem("All Videos", "all")
                self.playlist_combo.addItem("Recent Videos", "recent")
                self.playlist_combo.addItem("Other", "other_videos")
                
        except Exception as e:
            import logging
            logging.error(f"Error populating playlists: {str(e)}")
            
            # Default playlists as fallback
            self.playlist_combo.addItem("All Videos", "all")
            self.playlist_combo.addItem("Other", "other_videos")
        
    def on_queue_type_changed(self, index):
        """Handle queue type change."""
        queue_type = self.queue_type_combo.currentText()
        
        if queue_type == "Playlist Queue":
            self.playlist_combo.setEnabled(True)
            self.smart_options_group.setEnabled(False)
        elif queue_type == "Smart Queue":
            self.playlist_combo.setEnabled(False)
            self.smart_options_group.setEnabled(True)
        else:  # Custom Queue
            self.playlist_combo.setEnabled(False)
            self.smart_options_group.setEnabled(False)
        
    def create_queue(self):
        """Create the queue with selected parameters."""
        queue_type = self.queue_type_combo.currentText()
        
        # Validate weights sum to 100% for smart queue
        if queue_type == "Smart Queue":
            total_weight = (self.time_weight_spin.value() + 
                           self.popularity_weight_spin.value() + 
                           self.freshness_weight_spin.value())
            
            if total_weight != 100:
                QMessageBox.warning(
                    self, 
                    "Invalid Weights", 
                    f"Weights must sum to 100%. Current total: {total_weight}%"
                )
                return
        
        # Create queue parameters
        queue_params = {
            "type": queue_type,
            "limit": self.limit_spin.value(),
            "shuffle": self.shuffle_check.isChecked(),
            "include_history": self.include_history_check.isChecked()
        }
        
        if queue_type == "Playlist Queue":
            queue_params["playlist_id"] = self.playlist_combo.currentData()
            queue_params["playlist_name"] = self.playlist_combo.currentText()
            
        elif queue_type == "Smart Queue":
            queue_params["weights"] = {
                "time": self.time_weight_spin.value() / 100.0,
                "popularity": self.popularity_weight_spin.value() / 100.0,
                "freshness": self.freshness_weight_spin.value() / 100.0
            }
        
        # Emit signal with queue parameters
        self.queue_created.emit(queue_params)
        
        # Close dialog
        self.accept()