@echo off
:: Script to create a PyInstaller package for YouTube Playlist Downloader

echo Creating Python executable package with PyInstaller...
echo This may take a few minutes...

:: Install PyInstaller if not already installed
pip install -U pyinstaller

:: Create main executable
pyinstaller --name "YouTubePlaylistDownloader" ^
  --onedir ^
  --add-data "bin;bin" ^
  --add-data "downloader;downloader" ^
  --add-data "utils;utils" ^
  --add-data "gui_app;gui_app" ^
  --add-data "config.ini;." ^
  --add-data "README.md;." ^
  --hidden-import yt_dlp ^
  --hidden-import pydub ^
  --hidden-import ffmpeg ^
  --hidden-import configparser ^
  --hidden-import tkinter ^
  --noconsole ^
  main.py

:: Create GUI executable
pyinstaller --name "YouTubePlaylistDownloader-GUI" ^
  --onedir ^
  --add-data "bin;bin" ^
  --add-data "downloader;downloader" ^
  --add-data "utils;utils" ^
  --add-data "gui_app;gui_app" ^
  --add-data "config.ini;." ^
  --add-data "README.md;." ^
  --hidden-import yt_dlp ^
  --hidden-import pydub ^
  --hidden-import ffmpeg ^
  --hidden-import configparser ^
  --hidden-import tkinter ^
  --noconsole ^
  gui_app\launcher.py

echo PyInstaller packages created!
echo.
echo Creating final distribution folder...

:: Create dist folder
if not exist "dist\YouTubePlaylistDownloader-Full" mkdir "dist\YouTubePlaylistDownloader-Full"

:: Copy files to final distribution folder
xcopy /E /I /Y "dist\YouTubePlaylistDownloader\*" "dist\YouTubePlaylistDownloader-Full\"

:: Also copy the GUI executable
xcopy /E /I /Y "dist\YouTubePlaylistDownloader-GUI\*" "dist\YouTubePlaylistDownloader-Full\"

:: Create necessary empty folders
if not exist "dist\YouTubePlaylistDownloader-Full\data" mkdir "dist\YouTubePlaylistDownloader-Full\data"
if not exist "dist\YouTubePlaylistDownloader-Full\data\audio" mkdir "dist\YouTubePlaylistDownloader-Full\data\audio"

:: Create empty configuration files if they don't exist
if not exist "dist\YouTubePlaylistDownloader-Full\gui_app\playlists.json" (
    echo {"playlists": []} > "dist\YouTubePlaylistDownloader-Full\gui_app\playlists.json"
)
if not exist "dist\YouTubePlaylistDownloader-Full\gui_app\download_history.json" (
    echo {"videos": {}, "last_updated": ""} > "dist\YouTubePlaylistDownloader-Full\gui_app\download_history.json"
)

:: Create a simple installer batch file
echo @echo off > "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Installing YouTube Playlist Downloader... >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo set /p INSTALL_DIR="Enter installation directory (or press Enter for default [%%USERPROFILE%%\YouTubePlaylistDownloader]): " >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo if "%%INSTALL_DIR%%"=="" set INSTALL_DIR=%%USERPROFILE%%\YouTubePlaylistDownloader >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Creating installation directory... >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Copying files to %%INSTALL_DIR%%... >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo xcopy /E /I /Y * "%%INSTALL_DIR%%" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Creating shortcuts... >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Set oWS = WScript.CreateObject("WScript.Shell") > "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo sLinkFile = "%%USERPROFILE%%\Desktop\YouTube Playlist Downloader.lnk" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.TargetPath = "%%INSTALL_DIR%%\YouTubePlaylistDownloader-GUI.exe" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.WorkingDirectory = "%%INSTALL_DIR%%" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.Description = "YouTube Playlist Downloader" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.Save >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Set oWS = WScript.CreateObject("WScript.Shell") >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo sLinkFile = "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\YouTube Playlist Downloader.lnk" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.TargetPath = "%%INSTALL_DIR%%\YouTubePlaylistDownloader-GUI.exe" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.WorkingDirectory = "%%INSTALL_DIR%%" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.Description = "YouTube Playlist Downloader" >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo oLink.Save >> "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo cscript /nologo "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo del "%%TEMP%%\CreateShortcut.vbs" >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo Installation complete! >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo You can find YouTube Playlist Downloader at: %%INSTALL_DIR%% >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo echo. >> "dist\YouTubePlaylistDownloader-Full\install.bat"
echo pause >> "dist\YouTubePlaylistDownloader-Full\install.bat"

:: Create uninstaller
echo @echo off > "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Uninstalling YouTube Playlist Downloader... >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo set /p CONFIRM="Do you want to keep your downloaded files and playlist data? (Y/N): " >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo if /i "%%CONFIRM%%" == "Y" goto :KEEP_DATA >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo if /i "%%CONFIRM%%" == "y" goto :KEEP_DATA >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Removing shortcuts... >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo del "%%USERPROFILE%%\Desktop\YouTube Playlist Downloader.lnk" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo del "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\YouTube Playlist Downloader.lnk" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Removing installation directory... >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo rd /s /q "%%~dp0" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo goto :EOF >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo :KEEP_DATA >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Keeping data files... >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Removing shortcuts... >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo del "%%USERPROFILE%%\Desktop\YouTube Playlist Downloader.lnk" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo del "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\YouTube Playlist Downloader.lnk" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo xcopy /E /I /Y "%%~dp0\data" "%%TEMP%%\YTD_DataBackup\data" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo xcopy /E /I /Y "%%~dp0\gui_app\download_history.json" "%%TEMP%%\YTD_DataBackup\gui_app\" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo xcopy /E /I /Y "%%~dp0\gui_app\playlists.json" "%%TEMP%%\YTD_DataBackup\gui_app\" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Data files have been preserved in %%TEMP%%\YTD_DataBackup >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Please copy them to a safe location before closing this window. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo After pressing any key, the application will be uninstalled. >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo pause >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo echo Removing installation directory... >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"
echo rd /s /q "%%~dp0" >> "dist\YouTubePlaylistDownloader-Full\uninstall.bat"

:: Create a README.txt for the distribution
echo YouTube Playlist Downloader > "dist\YouTubePlaylistDownloader-Full\README.txt"
echo ============================= >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo. >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo This package contains the YouTube Playlist Downloader application. >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo. >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo Installation: >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo 1. Run install.bat >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo 2. Choose an installation directory or press Enter for the default >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo 3. Desktop and Start Menu shortcuts will be created automatically >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo. >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo Usage: >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo - Use the GUI application to manage playlists and settings >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo - YouTubePlaylistDownloader.exe is the console application >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo - YouTubePlaylistDownloader-GUI.exe is the graphical interface >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo. >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo Uninstallation: >> "dist\YouTubePlaylistDownloader-Full\README.txt"
echo Run uninstall.bat from the installation directory >> "dist\YouTubePlaylistDownloader-Full\README.txt"

echo.
echo Package creation complete! Your distribution is ready in "dist\YouTubePlaylistDownloader-Full"
echo You can zip this folder and distribute it to users.
echo.
pause