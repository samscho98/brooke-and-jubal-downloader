#!/usr/bin/env python3
"""
Test script to verify FFmpeg setup
"""
import os
import sys
import subprocess

def test_ffmpeg():
    """Test if FFmpeg is correctly set up"""
    print("Testing FFmpeg setup...")
    
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for FFmpeg in the bin directory
    bin_dir = os.path.join(project_dir, "bin")
    ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe" if os.name == 'nt' else "ffmpeg")
    
    # Test bundled FFmpeg
    if os.path.exists(ffmpeg_exe):
        print(f"Found bundled FFmpeg: {ffmpeg_exe}")
        
        # Check if it's executable (Unix)
        if os.name == 'posix':
            if not os.access(ffmpeg_exe, os.X_OK):
                print("FFmpeg is not executable, fixing permissions...")
                os.chmod(ffmpeg_exe, 0o755)
        
        # Try to run FFmpeg
        try:
            result = subprocess.run(
                [ffmpeg_exe, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print("Bundled FFmpeg is working correctly!")
                print(f"Version info: {result.stdout.splitlines()[0]}")
                return True
            else:
                print(f"Error running bundled FFmpeg: {result.stderr}")
        except Exception as e:
            print(f"Error testing bundled FFmpeg: {str(e)}")
    else:
        print(f"Bundled FFmpeg not found at: {ffmpeg_exe}")
    
    # Test system FFmpeg as a fallback
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("System FFmpeg is working correctly!")
            print(f"Version info: {result.stdout.splitlines()[0]}")
            print("\nYou can copy this FFmpeg to your application:")
            if os.name == 'nt':
                print(f"copy \"{os.path.dirname(result.stdout.split('ffmpeg version')[0])}\\ffmpeg.exe\" \"{bin_dir}\\ffmpeg.exe\"")
            else:
                import shutil
                ffmpeg_path = shutil.which("ffmpeg")
                print(f"cp \"{ffmpeg_path}\" \"{bin_dir}/ffmpeg\"")
                print(f"chmod +x \"{bin_dir}/ffmpeg\"")
            
            return True
        else:
            print("System FFmpeg not found or not working")
    except Exception as e:
        print("System FFmpeg not found")
    
    print("\nFFmpeg is not correctly set up. Please install FFmpeg manually.")
    print("Download FFmpeg from: https://ffmpeg.org/download.html")
    print(f"Place the executable in the 'bin' directory: {bin_dir}")
    
    return False

if __name__ == "__main__":
    test_ffmpeg()