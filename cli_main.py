#!/usr/bin/env python3
"""
Command-line interface entry point for YouTube Playlist Downloader.
"""
import sys
from cli.app import CLIApp

def main():
    """Run the CLI application."""
    app = CLIApp()
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