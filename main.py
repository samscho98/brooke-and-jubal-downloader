#!/usr/bin/env python3
"""
Main entry point for YouTube Playlist Downloader application.
Provides command-line interface and launches appropriate version (CLI or GUI).
"""
import sys
import argparse

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="YouTube Playlist Downloader")
    parser.add_argument("--no-gui", action="store_true", help="Run in command-line mode")
    parser.add_argument("--config", type=str, default="config.ini", help="Path to config file")
    
    # Parse just the GUI-related arguments first
    args, remaining = parser.parse_known_args()
    
    if args.no_gui:
        # Launch CLI version
        from cli.app import CLIApp
        app = CLIApp(config_path=args.config)
        return app.run()
    else:
        # Launch GUI version - if it's not implemented yet, fall back to CLI
        try:
            # Try to import the GUI module
            from gui.sidebar_app import launch_gui
            return launch_gui(config_path=args.config)
        except ImportError:
            print("GUI version not implemented yet or missing dependencies. Running CLI version.")
            from cli.app import CLIApp
            app = CLIApp(config_path=args.config)
            return app.run()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        import logging
        logging.exception("Unhandled exception")
        print(f"\nError: {str(e)}")
        sys.exit(1)