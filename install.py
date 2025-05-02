import os
import subprocess
import sys
import platform

def main():
    print("Installing YouTube Playlist Downloader...")
    
    # Create virtual environment
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    
    # Activate virtual environment and install requirements
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
    
    # Check for FFmpeg
    try:
        subprocess.check_call(["ffmpeg", "-version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        print("FFmpeg found on system path.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("WARNING: FFmpeg not found on system path.")
        print("Please install FFmpeg or place ffmpeg.exe in the bin/ directory.")
    
    print("\nInstallation complete!")
    print("Run the program with:")
    print(f"  {python_path} main.py           # For console interface")
    print(f"  {python_path} gui_app/launcher.py  # For GUI interface")

if __name__ == "__main__":
    main()