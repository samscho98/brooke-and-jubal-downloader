#!/usr/bin/env python3
"""
Launcher for YouTube Playlist Downloader GUI
This is the main entry point for non-technical users
"""
import os
import sys
import tkinter as tk
from pathlib import Path

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set up FFmpeg path before importing any other modules
bin_dir = os.path.join(current_dir, "bin")
ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")

# Set environment variables for FFmpeg
os.environ["FFMPEG_BINARY"] = ffmpeg_exe

# For pydub to use our FFmpeg
os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")

# Import the GUI
from gui_app.settings_gui import PlaylistDownloaderGUI

def main():
    """Main entry point for the application"""
    try:
        # Create the root window
        root = tk.Tk()
        root.title("YouTube Playlist Downloader")
        
        # Exception handler for showing errors to users
        def show_error(exc_type, exc_value, exc_traceback):
            import traceback
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"Error: {error_msg}")
            
            # Show error in a message box
            try:
                from tkinter import messagebox
                messagebox.showerror("Error", 
                                    f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
                                    f"Please check the error_log.txt file for details.")
                
                # Save error to log file in the same directory as the executable
                with open("error_log.txt", "a") as f:
                    from datetime import datetime
                    f.write(f"=== Error on {datetime.now()} ===\n")
                    f.write(error_msg)
                    f.write("\n\n")
            except:
                pass
                
        # Set up global exception handler
        sys.excepthook = show_error
        
        # Initialize the application
        app = PlaylistDownloaderGUI(root)
        
        # Set window icon if available
        icon_path = os.path.join(current_dir, "gui_app", "resources", "icon.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except:
                pass
        
        # Start the main loop
        root.mainloop()
        
        return 0
        
    except Exception as e:
        import traceback
        print(f"Error starting application: {str(e)}")
        traceback.print_exc()
        
        # Try to show a messagebox
        try:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error starting application: {str(e)}")
        except:
            pass
            
        return 1

if __name__ == "__main__":
    sys.exit(main())