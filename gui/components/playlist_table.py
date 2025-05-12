"""Table for displaying and managing playlists."""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class PlaylistTable(QTableWidget):
    """Table for displaying and managing playlists."""
    update_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    # Implementation
