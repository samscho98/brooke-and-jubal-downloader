"""
Settings Panel Component
Manages the settings configuration interface in the GUI application
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SettingsPanel(ttk.Frame):
    """Panel for configuring application settings"""
    
    def __init__(self, parent, config):
        """
        Initialize the settings panel
        
        Args:
            parent: Parent widget
            config: ConfigHandler instance
        """
        super().__init__(parent, padding="10")
        self.config = config
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the settings configuration widgets"""
        # Create settings grid
        row = 0
        
        # Output directory setting
        ttk.Label(self, text="Output Directory:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir_var = tk.StringVar(value=self.config.get("general", "output_directory"))
        ttk.Entry(self, textvariable=self.output_dir_var, width=50).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(self, text="Browse...", command=self._browse_output_dir).grid(row=row, column=2, padx=5, pady=5)
        row += 1
        
        # Default check interval
        ttk.Label(self, text="Default Check Interval (hours):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.check_interval_var = tk.StringVar(value=self.config.get("general", "check_interval", "24"))
        ttk.Entry(self, textvariable=self.check_interval_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Max downloads setting
        ttk.Label(self, text="Max Downloads Per Run:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_downloads_var = tk.StringVar(value=self.config.get("general", "max_downloads", "10"))
        ttk.Entry(self, textvariable=self.max_downloads_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Separator for audio settings
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1
        
        # Audio settings header
        ttk.Label(self, text="Audio Settings", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Audio format
        ttk.Label(self, text="Audio Format:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.audio_format_var = tk.StringVar(value=self.config.get("audio", "format", "mp3"))
        ttk.Combobox(self, textvariable=self.audio_format_var, values=["mp3", "m4a", "wav", "ogg"]).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Audio bitrate
        ttk.Label(self, text="Audio Bitrate:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.audio_bitrate_var = tk.StringVar(value=self.config.get("audio", "bitrate", "192k"))
        ttk.Combobox(self, textvariable=self.audio_bitrate_var, values=["128k", "192k", "256k", "320k"]).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Normalize audio checkbox
        self.normalize_audio_var = tk.BooleanVar(value=self.config.getboolean("audio", "normalize_audio", True))
        ttk.Checkbutton(self, text="Normalize Audio", variable=self.normalize_audio_var, command=self._toggle_normalize).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Target level (only enabled if normalize_audio is checked)
        ttk.Label(self, text="Target Level (dB):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.target_level_var = tk.StringVar(value=self.config.get("audio", "target_level", "-18.0"))
        self.target_level_entry = ttk.Entry(self, textvariable=self.target_level_var, width=10)
        self.target_level_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        self._toggle_normalize()  # Set initial state
        row += 1
        
        # Separator for logging settings
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1
        
        # Logging settings header
        ttk.Label(self, text="Logging Settings", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Logging level
        ttk.Label(self, text="Logging Level:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.log_level_var = tk.StringVar(value=self.config.get("logging", "level", "INFO"))
        ttk.Combobox(self, textvariable=self.log_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Log to console checkbox
        self.log_to_console_var = tk.BooleanVar(value=self.config.getboolean("logging", "console", True))
        ttk.Checkbutton(self, text="Log to Console", variable=self.log_to_console_var).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Log file
        ttk.Label(self, text="Log File:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.log_file_var = tk.StringVar(value=self.config.get("logging", "file", "app.log"))
        ttk.Entry(self, textvariable=self.log_file_var, width=30).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(self, text="Browse...", command=self._browse_log_file).grid(row=row, column=2, padx=5, pady=5)
        row += 1
        
        # Status frame at the bottom
        status_frame = ttk.LabelFrame(self, text="Settings Status")
        status_frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=10)
        row += 1
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Add a save button directly to the settings panel
        save_button_frame = ttk.Frame(self)
        save_button_frame.grid(row=row, column=0, columnspan=3, sticky=tk.E, padx=5, pady=10)
        
        ttk.Button(
            save_button_frame, 
            text="Save Settings",
            command=self.save_settings
        ).pack(side=tk.RIGHT, padx=5)
        
    def _toggle_normalize(self):
        """Toggle the target level entry based on normalize audio checkbox"""
        if self.normalize_audio_var.get():
            self.target_level_entry.configure(state="normal")
        else:
            self.target_level_entry.configure(state="disabled")
    
    def _browse_output_dir(self):
        """Open file dialog to browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def _browse_log_file(self):
        """Open file dialog to browse for log file"""
        filename = filedialog.asksaveasfilename(
            initialfile=self.log_file_var.get(),
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        if filename:
            self.log_file_var.set(filename)
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            # Validate inputs
            try:
                check_interval = int(self.check_interval_var.get())
                if check_interval <= 0:
                    raise ValueError("Check interval must be a positive number")
            except ValueError:
                messagebox.showerror("Error", "Check interval must be a positive number")
                return False
                
            try:
                max_downloads = int(self.max_downloads_var.get())
                if max_downloads <= 0:
                    raise ValueError("Max downloads must be a positive number")
            except ValueError:
                messagebox.showerror("Error", "Max downloads must be a positive number")
                return False
                
            if self.normalize_audio_var.get():
                try:
                    target_level = float(self.target_level_var.get())
                    if target_level > 0:
                        messagebox.showwarning("Warning", "Target level is typically a negative value (e.g., -18.0 dB)")
                except ValueError:
                    messagebox.showerror("Error", "Target level must be a number (e.g., -18.0)")
                    return False
            
            # Create output directory if it doesn't exist
            output_dir = self.output_dir_var.get()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # General settings
            self.config.set("general", "output_directory", self.output_dir_var.get())
            self.config.set("general", "check_interval", self.check_interval_var.get())
            self.config.set("general", "max_downloads", self.max_downloads_var.get())
            
            # Audio settings
            self.config.set("audio", "format", self.audio_format_var.get())
            self.config.set("audio", "bitrate", self.audio_bitrate_var.get())
            self.config.set("audio", "normalize_audio", str(self.normalize_audio_var.get()))
            self.config.set("audio", "target_level", self.target_level_var.get())
            
            # Logging settings
            self.config.set("logging", "level", self.log_level_var.get())
            self.config.set("logging", "file", self.log_file_var.get())
            self.config.set("logging", "console", str(self.log_to_console_var.get()))
            
            success = self.config.save_config()
            
            if success:
                self.status_var.set("Settings saved successfully")
                messagebox.showinfo("Success", "Settings saved successfully")
                return True
            else:
                self.status_var.set("Failed to save settings")
                return False
                
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            return False