"""Dialog for adding a new playlist."""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton
from PyQt5.QtCore import pyqtSignal

class AddPlaylistDialog(QDialog):
    """Dialog for adding a new playlist to track."""
    playlist_added = pyqtSignal(str, str, int)
    # Implementation
