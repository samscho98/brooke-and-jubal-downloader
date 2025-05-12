"""
Enhanced table for displaying the audio queue.
"""
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QMenu, QAction, 
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal

class QueueTable(QTableWidget):
    """Enhanced table for displaying and managing the audio queue."""
    
    play_requested = pyqtSignal(int)  # Row index
    remove_requested = pyqtSignal(int)  # Row index
    
    def __init__(self, parent=None):
        super().__init__(0, 5, parent)  # 5 columns
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        # Set up headers
        self.setHorizontalHeaderLabels(["#", "Title", "Playlist", "Duration", "Score"])
        self.verticalHeader().setVisible(False)
        
        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number column
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Title
        header.setSectionResizeMode(2, QHeaderView.Interactive)       # Playlist
        header.resizeSection(2, 200)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Duration
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Score
        
        # Configure selection
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set styles
        self.setStyleSheet("""
            QHeaderView::section {
                background-color: #121A21;
                color: white;
                padding: 4px;
                border: none;
            }
            QTableWidget {
                gridline-color: #2A2A2A;
            }
        """)
    
    def show_context_menu(self, position):
        """Show context menu for the queue table."""
        menu = QMenu()
        
        # Only show context menu if a row is selected
        if not self.selectedItems():
            return
            
        current_row = self.currentRow()
        
        # Add actions
        play_action = QAction("Play", self)
        play_action.triggered.connect(lambda: self.play_requested.emit(current_row))
        
        remove_action = QAction("Remove from Queue", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(current_row))
        
        # Add actions to menu
        menu.addAction(play_action)
        menu.addSeparator()
        menu.addAction(remove_action)
        
        # Show menu
        menu.exec_(self.viewport().mapToGlobal(position))