"""Settings page for the YouTube Playlist Downloader."""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QGroupBox, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QHBoxLayout, QFormLayout, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from data.config_manager import ConfigHandler
from downloader.youtube import YouTubeDownloader

class SettingsPage(QWidget):
    """Settings management page."""
    settings_saved = pyqtSignal()
    
    def __init__(self, config: ConfigHandler, downloader: YouTubeDownloader):
        super().__init__()
        self.config = config
        self.downloader = downloader
        
        # Initialize UI
        self.init_ui()
        
        # Load current config values
        self.load_settings()
    
    def init_ui(self):
        """Initialize user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1a2129;
                background-color: #121920;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #1a2129;
                color: white;
                padding: 8px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
            }
            QTabBar::tab:hover:!selected {
                background-color: #2a4055;
            }
        """)
        
        # Create tab pages
        general_tab = self.create_general_tab()
        audio_tab = self.create_audio_tab()
        player_tab = self.create_player_tab()
        scoring_tab = self.create_scoring_tab()
        advanced_tab = self.create_advanced_tab()
        
        # Add tabs
        self.tabs.addTab(general_tab, "General")
        self.tabs.addTab(audio_tab, "Audio")
        self.tabs.addTab(player_tab, "Player")
        self.tabs.addTab(scoring_tab, "Scoring")
        self.tabs.addTab(advanced_tab, "Advanced")
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #2a4055;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3a5065;
            }
            QPushButton:pressed {
                background-color: #1a3045;
            }
        """)
        
        # Set icon if available
        icon_path = os.path.join("gui", "icons", "refresh.svg")
        if os.path.exists(icon_path):
            self.reset_button.setIcon(QIcon(icon_path))
            self.reset_button.setIconSize(QSize(16, 16))
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3a92ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        
        # Set icon if available (could use a save icon if you have one)
        icon_path = os.path.join("gui", "icons", "download.svg")  # Using download as a substitute for save
        if os.path.exists(icon_path):
            self.save_button.setIcon(QIcon(icon_path))
            self.save_button.setIconSize(QSize(16, 16))
        
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        
        # Add tab widget and buttons to main layout
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(buttons_layout)
        
        # Connect signals
        self.reset_button.clicked.connect(self.reset_settings)
        self.save_button.clicked.connect(self.save_settings)

    def create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Output Directory Group
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout(output_group)
        
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Path to save downloaded files")
        self.output_dir_input.setReadOnly(True)
        
        browse_button = QPushButton("Browse...")
        browse_button.setFixedWidth(100)
        browse_button.clicked.connect(self.browse_output_directory)
        
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(browse_button)
        
        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)
        
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(1, 168)  # 1 hour to 7 days
        self.check_interval_spin.setSuffix(" hours")
        self.check_interval_spin.setToolTip("How often to check for new videos in tracked playlists")
        
        self.max_downloads_spin = QSpinBox()
        self.max_downloads_spin.setRange(1, 100)
        self.max_downloads_spin.setToolTip("Maximum number of videos to download at once")
        
        download_layout.addRow("Check Interval:", self.check_interval_spin)
        download_layout.addRow("Max Downloads:", self.max_downloads_spin)
        
        # User Interface Group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.dark_theme_check = QCheckBox("Use Dark Theme")
        self.dark_theme_check.setToolTip("Enable dark theme for the application")
        self.dark_theme_check.setChecked(True)  # Default to dark theme
        
        self.startup_page_combo = QComboBox()
        self.startup_page_combo.addItems(["Audio Player", "Playlists", "Analytics", "Settings", "About"])
        self.startup_page_combo.setToolTip("The page to show when the application starts")
        
        ui_layout.addRow("", self.dark_theme_check)
        ui_layout.addRow("Startup Page:", self.startup_page_combo)
        
        # Add groups to layout
        layout.addWidget(output_group)
        layout.addWidget(download_group)
        layout.addWidget(ui_group)
        layout.addStretch()
        
        return tab
    
    def create_audio_tab(self):
        """Create the audio settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Audio Format Group
        format_group = QGroupBox("Audio Format")
        format_layout = QFormLayout(format_group)
        
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "m4a", "ogg", "wav", "flac"])
        self.audio_format_combo.setToolTip("Format to use for downloaded audio files")
        
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["64k", "128k", "192k", "256k", "320k"])
        self.audio_bitrate_combo.setCurrentText("192k")  # Default to 192k
        self.audio_bitrate_combo.setToolTip("Bitrate for downloaded audio files")
        
        format_layout.addRow("Format:", self.audio_format_combo)
        format_layout.addRow("Bitrate:", self.audio_bitrate_combo)
        
        # Audio Processing Group
        processing_group = QGroupBox("Audio Processing")
        processing_layout = QFormLayout(processing_group)
        
        self.normalize_audio_check = QCheckBox()
        self.normalize_audio_check.setToolTip("Normalize audio levels for consistent volume")
        
        self.target_level_spin = QDoubleSpinBox()
        self.target_level_spin.setRange(-30.0, -1.0)
        self.target_level_spin.setDecimals(1)
        self.target_level_spin.setSingleStep(0.5)
        self.target_level_spin.setSuffix(" dB")
        self.target_level_spin.setToolTip("Target level for audio normalization")
        
        processing_layout.addRow("Normalize Audio:", self.normalize_audio_check)
        processing_layout.addRow("Target Level:", self.target_level_spin)
        
        # Add info box about normalization
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_frame.setStyleSheet("""
            #info_frame {
                background-color: #1a2129;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_text = (
            "<b>Audio Normalization</b><br><br>"
            "Normalizing audio adjusts the volume levels to make all tracks play at a similar volume. "
            "This is useful for playlists where some tracks might be louder than others.<br><br>"
            "The target level determines how loud the audio will be after normalization. "
            "Lower values (e.g., -18 dB) will be quieter but have more headroom."
        )
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #cccccc;")
        
        info_layout.addWidget(info_label)
        
        # Add groups to layout
        layout.addWidget(format_group)
        layout.addWidget(processing_group)
        layout.addWidget(info_frame)
        layout.addStretch()
        
        return tab
    
    def create_player_tab(self):
        """Create the player settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Playback Settings Group
        playback_group = QGroupBox("Playback Settings")
        playback_layout = QFormLayout(playback_group)
        
        self.default_playlist_combo = QComboBox()
        self.default_playlist_combo.addItems(["Latest", "Top Rated", "Random", "Custom"])
        self.default_playlist_combo.setToolTip("Default queue to load when the player starts")
        
        self.auto_normalize_check = QCheckBox()
        self.auto_normalize_check.setToolTip("Automatically normalize audio during playback")
        
        self.crossfade_check = QCheckBox()
        self.crossfade_check.setToolTip("Enable crossfade between tracks")
        
        self.crossfade_spin = QDoubleSpinBox()
        self.crossfade_spin.setRange(0.5, 5.0)
        self.crossfade_spin.setSingleStep(0.5)
        self.crossfade_spin.setSuffix(" seconds")
        self.crossfade_spin.setToolTip("Duration of crossfade between tracks")
        self.crossfade_spin.setEnabled(False)  # Disabled until checkbox checked
        
        playback_layout.addRow("Default Playlist:", self.default_playlist_combo)
        playback_layout.addRow("Auto-normalize:", self.auto_normalize_check)
        playback_layout.addRow("Enable Crossfade:", self.crossfade_check)
        playback_layout.addRow("Crossfade Duration:", self.crossfade_spin)
        
        # History Group
        history_group = QGroupBox("Playback History")
        history_layout = QFormLayout(history_group)
        
        self.keep_history_check = QCheckBox()
        self.keep_history_check.setToolTip("Keep track of playback history")
        
        self.history_limit_spin = QSpinBox()
        self.history_limit_spin.setRange(10, 1000)
        self.history_limit_spin.setSingleStep(10)
        self.history_limit_spin.setSuffix(" tracks")
        self.history_limit_spin.setToolTip("Maximum number of tracks to keep in history")
        
        clear_history_button = QPushButton("Clear History")
        clear_history_button.setToolTip("Clear all playback history")
        clear_history_button.clicked.connect(self.clear_history_clicked)
        
        history_layout.addRow("Keep History:", self.keep_history_check)
        history_layout.addRow("History Limit:", self.history_limit_spin)
        history_layout.addRow("", clear_history_button)
        
        # Connect signals
        self.crossfade_check.toggled.connect(self.crossfade_spin.setEnabled)
        
        # Add groups to layout
        layout.addWidget(playback_group)
        layout.addWidget(history_group)
        layout.addStretch()
        
        return tab
    
    def create_scoring_tab(self):
        """Create the scoring settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scoring System Group
        scoring_group = QGroupBox("Scoring System")
        scoring_layout = QFormLayout(scoring_group)
        
        self.enable_scoring_check = QCheckBox()
        self.enable_scoring_check.setToolTip("Enable the intelligent scoring system")
        
        scoring_layout.addRow("Enable Scoring:", self.enable_scoring_check)
        
        # Scoring Parameters Group
        parameters_group = QGroupBox("Scoring Parameters")
        parameters_layout = QFormLayout(parameters_group)
        
        self.score_decay_spin = QDoubleSpinBox()
        self.score_decay_spin.setRange(0.1, 1.0)
        self.score_decay_spin.setDecimals(2)
        self.score_decay_spin.setSingleStep(0.05)
        self.score_decay_spin.setToolTip("How quickly scores decay over time (lower = faster decay)")
        
        self.new_content_boost_spin = QDoubleSpinBox()
        self.new_content_boost_spin.setRange(1.0, 3.0)
        self.new_content_boost_spin.setDecimals(1)
        self.new_content_boost_spin.setSingleStep(0.1)
        self.new_content_boost_spin.setToolTip("Boost factor for new content")
        
        self.time_effect_spin = QDoubleSpinBox()
        self.time_effect_spin.setRange(0.0, 2.0)
        self.time_effect_spin.setDecimals(1)
        self.time_effect_spin.setSingleStep(0.1)
        self.time_effect_spin.setToolTip("How strongly time-of-day affects scoring (0 = no effect)")
        
        parameters_layout.addRow("Score Decay:", self.score_decay_spin)
        parameters_layout.addRow("New Content Boost:", self.new_content_boost_spin)
        parameters_layout.addRow("Time Effect Strength:", self.time_effect_spin)
        
        # Add info box about scoring
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_frame.setStyleSheet("""
            #info_frame {
                background-color: #1a2129;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_text = (
            "<b>Scoring System</b><br><br>"
            "The scoring system determines the optimal order for playing audio files based on several factors:<br><br>"
            "• YouTube metadata (views, comments)<br>"
            "• Playback history and engagement<br>"
            "• Time-of-day effects<br>"
            "• Content freshness<br><br>"
            "<b>Parameters:</b><br>"
            "• <b>Score Decay</b>: How scores decrease over time to prevent repeating the same tracks<br>"
            "• <b>New Content Boost</b>: Extra score for recently added tracks<br>"
            "• <b>Time Effect</b>: How much time-of-day influences track selection"
        )
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #cccccc;")
        
        info_layout.addWidget(info_label)
        
        # Add groups to layout
        layout.addWidget(scoring_group)
        layout.addWidget(parameters_group)
        layout.addWidget(info_frame)
        layout.addStretch()
        
        return tab
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging Group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setToolTip("Logging level (higher = less verbose)")
        
        self.console_logging_check = QCheckBox()
        self.console_logging_check.setToolTip("Show log messages in console")
        
        self.log_file_check = QCheckBox()
        self.log_file_check.setToolTip("Save log messages to file")
        
        self.log_file_input = QLineEdit()
        self.log_file_input.setPlaceholderText("Path to log file")
        self.log_file_input.setReadOnly(True)
        
        browse_log_button = QPushButton("Browse...")
        browse_log_button.setFixedWidth(100)
        browse_log_button.clicked.connect(self.browse_log_file)
        
        log_file_layout = QHBoxLayout()
        log_file_layout.addWidget(self.log_file_input)
        log_file_layout.addWidget(browse_log_button)
        
        logging_layout.addRow("Log Level:", self.log_level_combo)
        logging_layout.addRow("Console Logging:", self.console_logging_check)
        logging_layout.addRow("File Logging:", self.log_file_check)
        logging_layout.addRow("Log File:", log_file_layout)
        
        # Advanced Options Group
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        self.concurrent_downloads_spin = QSpinBox()
        self.concurrent_downloads_spin.setRange(1, 5)
        self.concurrent_downloads_spin.setToolTip("Number of concurrent downloads (higher values may cause issues)")
        
        self.ffmpeg_path_input = QLineEdit()
        self.ffmpeg_path_input.setPlaceholderText("Path to FFmpeg executable (leave empty for default)")
        
        browse_ffmpeg_button = QPushButton("Browse...")
        browse_ffmpeg_button.setFixedWidth(100)
        browse_ffmpeg_button.clicked.connect(self.browse_ffmpeg_path)
        
        ffmpeg_layout = QHBoxLayout()
        ffmpeg_layout.addWidget(self.ffmpeg_path_input)
        ffmpeg_layout.addWidget(browse_ffmpeg_button)
        
        advanced_layout.addRow("Concurrent Downloads:", self.concurrent_downloads_spin)
        advanced_layout.addRow("FFmpeg Path:", ffmpeg_layout)
        
        # Warning label
        warning_label = QLabel(
            "<b>Warning:</b> Changing these settings may affect application stability. "
            "Only modify if you know what you're doing."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #cc3300;")
        
        # Add groups to layout
        layout.addWidget(logging_group)
        layout.addWidget(advanced_group)
        layout.addWidget(warning_label)
        layout.addStretch()
        
        # Connect signals
        self.log_file_check.toggled.connect(self.toggle_log_file)
        
        return tab
    
    def toggle_log_file(self, checked):
        """Handle log file checkbox toggle."""
        self.log_file_input.setEnabled(checked)
        
    def load_settings(self):
        """Load settings from config."""
        # General settings
        self.output_dir_input.setText(self.config.get("general", "output_directory", "data/audio"))
        self.check_interval_spin.setValue(self.config.getint("general", "check_interval", 24))
        self.max_downloads_spin.setValue(self.config.getint("general", "max_downloads", 10))
        
        # UI settings
        self.dark_theme_check.setChecked(self.config.getboolean("ui", "dark_theme", True))
        self.startup_page_combo.setCurrentText(self.config.get("ui", "startup_page", "Audio Player"))
        
        # Audio settings
        self.audio_format_combo.setCurrentText(self.config.get("audio", "format", "mp3"))
        self.audio_bitrate_combo.setCurrentText(self.config.get("audio", "bitrate", "192k"))
        self.normalize_audio_check.setChecked(self.config.getboolean("audio", "normalize_audio", False))
        self.target_level_spin.setValue(self.config.getfloat("audio", "target_level", -18.0))
        
        # Player settings
        self.default_playlist_combo.setCurrentText(self.config.get("player", "default_playlist", "Latest"))
        self.auto_normalize_check.setChecked(self.config.getboolean("player", "auto_normalize", False))
        self.crossfade_check.setChecked(self.config.getboolean("player", "crossfade", False))
        self.crossfade_spin.setValue(self.config.getfloat("player", "crossfade_duration", 2.0))
        self.crossfade_spin.setEnabled(self.crossfade_check.isChecked())
        
        self.keep_history_check.setChecked(self.config.getboolean("player", "keep_history", True))
        self.history_limit_spin.setValue(self.config.getint("player", "history_limit", 100))
        
        # Scoring settings
        self.enable_scoring_check.setChecked(self.config.getboolean("scoring", "enable_scoring", True))
        self.score_decay_spin.setValue(self.config.getfloat("scoring", "score_decay", 0.9))
        self.new_content_boost_spin.setValue(self.config.getfloat("scoring", "new_content_boost", 1.5))
        self.time_effect_spin.setValue(self.config.getfloat("scoring", "time_effect_strength", 1.0))
        
        # Logging settings
        self.log_level_combo.setCurrentText(self.config.get("logging", "level", "INFO"))
        self.console_logging_check.setChecked(self.config.getboolean("logging", "console", True))
        self.log_file_check.setChecked(self.config.getboolean("logging", "file_logging", False))
        self.log_file_input.setText(self.config.get("logging", "file", "logs/app.log"))
        self.log_file_input.setEnabled(self.log_file_check.isChecked())
        
        # Advanced settings
        self.concurrent_downloads_spin.setValue(self.config.getint("advanced", "concurrent_downloads", 1))
        self.ffmpeg_path_input.setText(self.config.get("advanced", "ffmpeg_path", ""))
        
    def save_settings(self):
        """Save settings to config."""
        # General settings
        self.config.set("general", "output_directory", self.output_dir_input.text())
        self.config.set("general", "check_interval", str(self.check_interval_spin.value()))
        self.config.set("general", "max_downloads", str(self.max_downloads_spin.value()))
        
        # UI settings
        self.config.set("ui", "dark_theme", str(self.dark_theme_check.isChecked()))
        self.config.set("ui", "startup_page", self.startup_page_combo.currentText())
        
        # Audio settings
        self.config.set("audio", "format", self.audio_format_combo.currentText())
        self.config.set("audio", "bitrate", self.audio_bitrate_combo.currentText())
        self.config.set("audio", "normalize_audio", str(self.normalize_audio_check.isChecked()))
        self.config.set("audio", "target_level", str(self.target_level_spin.value()))
        
        # Player settings
        self.config.set("player", "default_playlist", self.default_playlist_combo.currentText())
        self.config.set("player", "auto_normalize", str(self.auto_normalize_check.isChecked()))
        self.config.set("player", "crossfade", str(self.crossfade_check.isChecked()))
        self.config.set("player", "crossfade_duration", str(self.crossfade_spin.value()))
        
        self.config.set("player", "keep_history", str(self.keep_history_check.isChecked()))
        self.config.set("player", "history_limit", str(self.history_limit_spin.value()))
        
        # Scoring settings
        self.config.set("scoring", "enable_scoring", str(self.enable_scoring_check.isChecked()))
        self.config.set("scoring", "score_decay", str(self.score_decay_spin.value()))
        self.config.set("scoring", "new_content_boost", str(self.new_content_boost_spin.value()))
        self.config.set("scoring", "time_effect_strength", str(self.time_effect_spin.value()))
        
        # Logging settings
        self.config.set("logging", "level", self.log_level_combo.currentText())
        self.config.set("logging", "console", str(self.console_logging_check.isChecked()))
        self.config.set("logging", "file_logging", str(self.log_file_check.isChecked()))
        self.config.set("logging", "file", self.log_file_input.text())
        
        # Advanced settings
        self.config.set("advanced", "concurrent_downloads", str(self.concurrent_downloads_spin.value()))
        self.config.set("advanced", "ffmpeg_path", self.ffmpeg_path_input.text())
        
        # Save config
        if self.config.save_config():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully")
            
            # Emit signal that settings were saved
            self.settings_saved.emit()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Failed to save settings")
        
    def reset_settings(self):
        """Reset settings to defaults."""
        from PyQt5.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Reset config to defaults
            self.config.reset_to_default()
            
            # Reload settings
            self.load_settings()
            
            QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults")
        
    def browse_output_directory(self):
        """Show file browser to select output directory."""
        from PyQt5.QtWidgets import QFileDialog
        
        current_dir = self.output_dir_input.text()
        if not current_dir:
            current_dir = os.path.expanduser("~")
            
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir
        )
        
        if directory:
            self.output_dir_input.setText(directory)
        
    def browse_log_file(self):
        """Show file browser to select log file."""
        from PyQt5.QtWidgets import QFileDialog
        
        current_file = self.log_file_input.text()
        current_dir = os.path.dirname(current_file) if current_file else "logs"
        
        if not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            current_dir,
            "Log Files (*.log);;All Files (*.*)"
        )
        
        if file_name:
            self.log_file_input.setText(file_name)
        
    def browse_ffmpeg_path(self):
        """Show file browser to select FFmpeg path."""
        from PyQt5.QtWidgets import QFileDialog
        
        current_path = self.ffmpeg_path_input.text()
        current_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
            
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select FFmpeg Executable",
            current_dir,
            "Executable Files (*.exe);;All Files (*.*)"
        )
        
        if file_name:
            self.ffmpeg_path_input.setText(file_name)
        
    def clear_history_clicked(self):
        """Handle clear history button click."""
        from PyQt5.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self, 
            "Clear History", 
            "Are you sure you want to clear all playback history?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Clear history in scoring system
                if hasattr(self.downloader, 'scoring') and self.downloader.scoring:
                    if hasattr(self.downloader.scoring, 'calculator') and self.downloader.scoring.calculator:
                        if hasattr(self.downloader.scoring.calculator, 'scores_data'):
                            # Clear play history
                            self.downloader.scoring.calculator.scores_data["play_history"] = []
                            
                            # Reset play counts
                            for video_id in self.downloader.scoring.calculator.scores_data["videos"]:
                                self.downloader.scoring.calculator.scores_data["videos"][video_id]["play_count"] = 0
                                self.downloader.scoring.calculator.scores_data["videos"][video_id]["last_played"] = None
                            
                            # Save changes
                            self.downloader.scoring.calculator._save_scores()
                            
                QMessageBox.information(self, "History Cleared", "Playback history has been cleared")
            except Exception as e:
                import logging
                logging.error(f"Error clearing history: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to clear history: {str(e)}")