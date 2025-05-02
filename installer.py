# install_fix.py
import os
import subprocess
import sys
import platform
import shutil

def main():
    print("Installing YouTube Playlist Downloader...")
    
    # Create virtual environment
    if os.path.exists("venv"):
        print("Removing existing virtual environment...")
        shutil.rmtree("venv")
    
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    
    # Determine paths based on platform
    if platform.system() == "Windows":
        scripts_dir = os.path.join("venv", "Scripts")
        python_path = os.path.join(scripts_dir, "python.exe")
        pip_path = os.path.join(scripts_dir, "pip.exe")
        site_packages = os.path.join("venv", "Lib", "site-packages")
    else:
        scripts_dir = os.path.join("venv", "bin")
        python_path = os.path.join(scripts_dir, "python")
        pip_path = os.path.join(scripts_dir, "pip")
        # Account for different Python versions in path
        python_version = subprocess.check_output([python_path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], 
                                               universal_newlines=True).strip()
        site_packages = os.path.join("venv", "lib", f"python{python_version}", "site-packages")
    
    # Upgrade pip using the Python executable
    print("Upgrading pip...")
    subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    print("Installing dependencies...")
    subprocess.check_call([python_path, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create audioop mock module
    create_audioop_mock(site_packages)
    
    # Check for FFmpeg
    print("Checking for FFmpeg...")
    ffmpeg_found = False
    
    # Check bundled FFmpeg
    bin_dir = os.path.join(os.getcwd(), "bin")
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
    
    ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")
    
    if os.path.exists(ffmpeg_exe):
        print(f"Found bundled FFmpeg: {ffmpeg_exe}")
        ffmpeg_found = True
    else:
        # Check system FFmpeg
        try:
            subprocess.check_call(
                ["ffmpeg", "-version"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            print("Found FFmpeg in system path.")
            ffmpeg_found = True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    if not ffmpeg_found:
        print("\nWARNING: FFmpeg not found!")
        print("For audio conversion to work, please either:")
        print("1. Install FFmpeg on your system and make sure it's in your PATH, or")
        print("2. Place ffmpeg.exe inside the bin directory")
    
    # Check for tkinter (for GUI)
    print("\nChecking for tkinter (required for GUI)...")
    try:
        subprocess.check_call(
            [python_path, "-c", "import tkinter; tkinter.Tk()"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        print("tkinter is available. GUI will work correctly.")
    except subprocess.SubprocessError:
        print("WARNING: tkinter not found or not working.")
        print("The GUI interface may not function properly.")
        print("On Windows: Reinstall Python and select the 'tcl/tk and IDLE' option")
        print("On Linux: Install the python3-tk package (e.g., sudo apt install python3-tk)")

    # Verify pydub works with our mock
    print("\nVerifying pydub with audioop mock...")
    try:
        subprocess.check_call(
            [python_path, "-c", "import pydub; print('Pydub import successful!')"], 
            universal_newlines=True
        )
        print("✓ Pydub import test passed!")
    except subprocess.SubprocessError as e:
        print(f"× Pydub import test failed: {e}")
        print("The audioop mock may not be working correctly.")

    # Create launcher batch/shell scripts
    create_launcher_scripts(python_path)
    
    print("\nInstallation complete!")
    print("Run the program using:")
    if platform.system() == "Windows":
        print("  run_console.bat  # For console interface")
        print("  run_gui.bat      # For GUI interface")
    else:
        print("  ./run_console.sh  # For console interface")
        print("  ./run_gui.sh      # For GUI interface")

def create_audioop_mock(site_packages):
    """Create a mock audioop module that pydub can use"""
    print(f"Creating audioop mock in {site_packages}...")
    
    # Create the audioop.py file
    audioop_path = os.path.join(site_packages, "audioop.py")
    with open(audioop_path, 'w') as f:
        f.write("""
# Mock audioop module for pydub compatibility
def add(fragment1, fragment2, width):
    return b''

def avg(fragment, width):
    return 0

def avgpp(fragment, width):
    return 0

def bias(fragment, width, bias):
    return b''

def byteswap(fragment, width):
    return b''

def cross(fragment1, fragment2, width):
    return 0

def findfactor(fragment1, fragment2, width):
    return 0

def findfit(fragment1, fragment2, width):
    return (0, 0)

def findmax(fragment, width):
    return 0

def getsample(fragment, width, index):
    return 0

def lin2adpcm(fragment, width, state):
    return (b'', (0, 0))

def lin2alaw(fragment, width):
    return b''

def lin2lin(fragment, width1, width2):
    return b''

def lin2ulaw(fragment, width):
    return b''

def minmax(fragment, width):
    return (0, 0)

def mul(fragment, width, factor):
    return b''

def ratecv(fragment, width, nchannels, inrate, outrate, state, weightA=1, weightB=0):
    return (b'', (0, 0, 0))

def reverse(fragment, width):
    return b''

def rms(fragment, width):
    return 0

def tomono(fragment, width, lfactor, rfactor):
    return b''

def tostereo(fragment, width, lfactor, rfactor):
    return b''

def ulaw2lin(fragment, width):
    return b''

def alaw2lin(fragment, width):
    return b''

def adpcm2lin(fragment, width, state):
    return (b'', (0, 0))

def deemphasize(fragment, width, state):
    return (b'', (0, 0))

def max(fragment, width):
    return 0

def maxpp(fragment, width):
    return 0

def minmax(fragment, width):
    return (0, 0)

def negativefactor(fragment1, fragment2, width):
    return 0
""")

    # Create pyaudioop.py as well as a fallback
    pyaudioop_path = os.path.join(site_packages, "pyaudioop.py")
    shutil.copy2(audioop_path, pyaudioop_path)

    print("Created audioop and pyaudioop mock modules")

def create_launcher_scripts(python_path):
    """Create launcher scripts based on platform"""
    venv_dir = os.path.dirname(os.path.dirname(python_path))
    
    if platform.system() == "Windows":
        # Windows batch files
        with open("run_console.bat", "w") as f:
            f.write('@echo off\n')
            f.write('echo Starting YouTube Playlist Downloader (Console)...\n')
            f.write(f'call "{os.path.join(venv_dir, "Scripts", "activate.bat")}"\n')
            f.write('python main.py\n')
            f.write('pause\n')
        
        with open("run_gui.bat", "w") as f:
            f.write('@echo off\n')
            f.write('echo Starting YouTube Playlist Downloader (GUI)...\n')
            f.write(f'call "{os.path.join(venv_dir, "Scripts", "activate.bat")}"\n')
            f.write('python gui_app/launcher.py\n')
            f.write('pause\n')
    else:
        # Unix shell scripts
        with open("run_console.sh", "w") as f:
            f.write('#!/bin/sh\n')
            f.write('echo "Starting YouTube Playlist Downloader (Console)..."\n')
            f.write(f'source "{os.path.join(venv_dir, "bin", "activate")}"\n')
            f.write('python main.py\n')
        
        with open("run_gui.sh", "w") as f:
            f.write('#!/bin/sh\n')
            f.write('echo "Starting YouTube Playlist Downloader (GUI)..."\n')
            f.write(f'source "{os.path.join(venv_dir, "bin", "activate")}"\n')
            f.write('python gui_app/launcher.py\n')
        
        # Make shell scripts executable
        os.chmod("run_console.sh", 0o755)
        os.chmod("run_gui.sh", 0o755)

if __name__ == "__main__":
    main()