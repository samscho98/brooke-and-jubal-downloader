"""Custom progress dialog for downloads and updates."""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class ProgressDialog(QDialog):
    """Custom progress dialog with cancel button."""
    canceled = pyqtSignal()
    # Implementation
