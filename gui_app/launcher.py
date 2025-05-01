#!/usr/bin/env python3
"""
GUI Launcher for YouTube Playlist Downloader
This script starts the settings GUI
"""
import os
import sys
import tkinter as tk
from pathlib import Path

# Add the parent directory to the path so we can import the GUI
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gui_app.settings_gui import PlaylistDownloaderGUI

def main():
    """Main entry point for the GUI application"""
    # Check if required modules are installed
    try:
        import tkinter as tk
    except ImportError:
        print("Error: tkinter is not installed.")
        print("On Windows, reinstall Python and select the tcl/tk option.")
        print("On Linux, install python3-tk package (e.g., sudo apt install python3-tk).")
        return 1

    try:
        # Create the root window
        root = tk.Tk()
        
        # Setup exception handler
        def show_error(exc_type, exc_value, exc_traceback):
            import traceback
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"Unhandled Exception:\n{error_msg}")
            
            # Show error in a message box if possible
            try:
                from tkinter import messagebox
                messagebox.showerror("Unhandled Exception", 
                                    f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
                                    f"Please check the console for details.")
            except:
                # If messagebox fails, we already printed to console
                pass
                
        # Set up global exception handler
        import sys
        sys.excepthook = show_error
        
        # Initialize the application
        app = PlaylistDownloaderGUI(root)
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except:
                # Not critical if icon fails to load
                pass
        
        # Start the main loop
        root.mainloop()
        
        return 0
        
    except Exception as e:
        import traceback
        print(f"Error starting GUI application: {str(e)}")
        traceback.print_exc()
        
        # Try to show a messagebox if tkinter is available
        try:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error starting application: {str(e)}")
        except:
            pass
            
        return 1

if __name__ == "__main__":
    sys.exit(main())