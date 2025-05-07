"""
Updater Panel Component
Manages the application update interface in the GUI application
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys

# Make sure parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.updater import Updater

class UpdaterPanel(ttk.Frame):
    """Panel for managing application updates"""
    
    def __init__(self, parent, current_version="1.0.0", repo_owner="samscho98", repo_name="youtube-playlist-downloader"):
        """
        Initialize the updater panel
        
        Args:
            parent: Parent widget
            current_version: Current version of the application
            repo_owner: GitHub repository owner username
            repo_name: GitHub repository name
        """
        super().__init__(parent, padding="20")
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.updater = Updater(repo_owner, repo_name, current_version)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the updater interface widgets"""
        # Application version display
        version_frame = ttk.Frame(self)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            version_frame, 
            text="YouTube Playlist Downloader", 
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 5))
        
        ttk.Label(
            version_frame,
            text=f"Version {self.current_version}",
            font=("Arial", 12)
        ).pack()
        
        # Update check section
        check_frame = ttk.LabelFrame(self, text="Update Checker", padding="10")
        check_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Version status
        self.version_status_var = tk.StringVar(value="Current version: " + self.current_version)
        ttk.Label(
            check_frame,
            textvariable=self.version_status_var,
            font=("Arial", 10, "bold")
        ).pack(fill=tk.X, pady=5)
        
        # Latest version info
        self.latest_version_var = tk.StringVar(value="Latest version: Checking...")
        ttk.Label(
            check_frame,
            textvariable=self.latest_version_var
        ).pack(fill=tk.X, pady=5)
        
        # Update status
        self.update_status_var = tk.StringVar(value="Status: Not checked")
        ttk.Label(
            check_frame,
            textvariable=self.update_status_var
        ).pack(fill=tk.X, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            check_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress.pack(fill=tk.X, pady=10)
        
        # Check for updates button
        button_frame = ttk.Frame(check_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.check_button = ttk.Button(
            button_frame,
            text="Check for Updates",
            command=self.check_for_updates
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        # Update button (initially disabled)
        self.update_button = ttk.Button(
            button_frame,
            text="Update Application",
            command=self.update_application,
            state=tk.DISABLED
        )
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        # Release notes section
        notes_frame = ttk.LabelFrame(self, text="Release Notes", padding="10")
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollable text area for release notes
        notes_scroll = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL)
        
        self.release_notes = tk.Text(
            notes_frame,
            yscrollcommand=notes_scroll.set,
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED
        )
        
        notes_scroll.config(command=self.release_notes.yview)
        
        self.release_notes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # GitHub link
        link_frame = ttk.Frame(self)
        link_frame.pack(fill=tk.X, pady=5)
        
        github_link = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        github_label = ttk.Label(
            link_frame,
            text=f"View on GitHub: {github_link}",
            foreground="blue",
            cursor="hand2"
        )
        github_label.pack(fill=tk.X)
        github_label.bind("<Button-1>", lambda e: self._open_url(github_link))
        
        # Auto-check for updates on panel creation
        self.after(1000, self.check_for_updates)
    
    def _set_release_notes(self, text):
        """Set the release notes text"""
        self.release_notes.config(state=tk.NORMAL)
        self.release_notes.delete(1.0, tk.END)
        self.release_notes.insert(tk.END, text)
        self.release_notes.config(state=tk.DISABLED)
    
    def _open_url(self, url):
        """Open a URL in the default web browser"""
        import webbrowser
        webbrowser.open(url)
    
    def check_for_updates(self):
        """Check for application updates"""
        # Disable buttons during check
        self.check_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.DISABLED)
        
        # Update UI
        self.update_status_var.set("Status: Checking for updates...")
        self.progress_var.set(10)
        
        # Start check in a separate thread
        def check_thread():
            try:
                # Check for updates
                update_available, latest_version, release_notes = self.updater.check_for_updates()
                
                # Update UI with results (in main thread)
                self.after(0, lambda: self._update_check_results(update_available, latest_version, release_notes))
                
            except Exception as e:
                # Handle errors (in main thread)
                error_msg = str(e)
                self.after(0, lambda: self._update_check_error(error_msg))
        
        thread = threading.Thread(target=check_thread)
        thread.daemon = True
        thread.start()
    
    def _update_check_results(self, update_available, latest_version, release_notes):
        """Update UI with check results"""
        self.latest_version_var.set(f"Latest version: {latest_version}")
        self.progress_var.set(100)
        
        if update_available:
            self.update_status_var.set(f"Status: Update available! ({latest_version})")
            self.update_button.config(state=tk.NORMAL)
            self._set_release_notes(release_notes)
        else:
            self.update_status_var.set("Status: You have the latest version")
            self._set_release_notes("You are using the latest version available.")
        
        # Re-enable check button
        self.check_button.config(state=tk.NORMAL)
    
    def _update_check_error(self, error_msg):
        """Update UI with check error"""
        self.update_status_var.set(f"Status: Error checking for updates")
        self.latest_version_var.set("Latest version: Unknown")
        self.progress_var.set(0)
        self._set_release_notes(f"Error checking for updates:\n\n{error_msg}")
        
        # Re-enable check button
        self.check_button.config(state=tk.NORMAL)
    
    def update_application(self):
        """Download and install update"""
        # Confirm the update
        if not messagebox.askyesno(
            "Confirm Update",
            "Do you want to update the application? The application will be restarted after the update.\n\n"
            "All unsaved changes will be lost.",
            parent=self
        ):
            return
        
        # Disable buttons during update
        self.check_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.DISABLED)
        
        # Update UI
        self.update_status_var.set("Status: Downloading update...")
        self.progress_var.set(20)
        
        # Start update in a separate thread
        def update_thread():
            try:
                # Update the application
                success = self.updater.update_application(auto_restart=False)
                
                # Update UI with results (in main thread)
                self.after(0, lambda: self._update_results(success))
                
            except Exception as e:
                # Handle errors (in main thread)
                error_msg = str(e)
                self.after(0, lambda: self._update_error(error_msg))
        
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
    
    def _update_results(self, success):
        """Update UI with update results"""
        self.progress_var.set(100)
        
        if success:
            self.update_status_var.set("Status: Update successful! Restart required.")
            
            # Ask to restart the application
            if messagebox.askyesno(
                "Update Complete",
                "The application has been updated successfully! Do you want to restart now?",
                parent=self
            ):
                self._restart_application()
        else:
            self.update_status_var.set("Status: Update failed")
            self._set_release_notes("Failed to update the application. Please try again later.")
        
        # Re-enable buttons
        self.check_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.NORMAL)
    
    def _update_error(self, error_msg):
        """Update UI with update error"""
        self.update_status_var.set("Status: Error updating application")
        self.progress_var.set(0)
        self._set_release_notes(f"Error updating application:\n\n{error_msg}")
        
        # Re-enable buttons
        self.check_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.NORMAL)
    
    def _restart_application(self):
        """Restart the application after update"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Running as script
            import subprocess
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            script_path = os.path.join(app_dir, "gui_app", "launcher.py")
            
            # Use the same Python interpreter to restart
            subprocess.Popen([sys.executable, script_path])
            
            # Close the current instance
            import tkinter
            root = self.winfo_toplevel()
            root.destroy()
            sys.exit(0)