; YouTubePlaylistDownloader Installer Script
!include "MUI2.nsh"

; General settings
Name "YouTube Playlist Downloader"
OutFile "YouTubePlaylistDownloader_Setup.exe"
InstallDir "$PROGRAMFILES\YouTubePlaylistDownloader"
InstallDirRegKey HKCU "Software\YouTubePlaylistDownloader" ""

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "gui_app\resources\icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation section
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Add the files to install
  File "dist\YouTubePlaylistDownloader.exe"
  
  ; Create directories
  CreateDirectory "$INSTDIR\data\audio"
  
  ; Create default config files
  FileOpen $0 "$INSTDIR\config.ini" w
  FileWrite $0 "[general]$\r$\n"
  FileWrite $0 "output_directory = $INSTDIR\data\audio$\r$\n"
  FileWrite $0 "check_interval = 24$\r$\n"
  FileWrite $0 "max_downloads = 10$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "[audio]$\r$\n"
  FileWrite $0 "format = mp3$\r$\n"
  FileWrite $0 "bitrate = 192k$\r$\n"
  FileWrite $0 "normalize_audio = True$\r$\n"
  FileWrite $0 "target_level = -18.0$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "[logging]$\r$\n"
  FileWrite $0 "level = INFO$\r$\n"
  FileWrite $0 "file = $INSTDIR\app.log$\r$\n"
  FileWrite $0 "console = True$\r$\n"
  FileClose $0
  
  ; Create empty playlists file
  FileOpen $0 "$INSTDIR\gui_app\playlists.json" w
  FileWrite $0 "{$\r$\n"
  FileWrite $0 "  $\"playlists$\": []$\r$\n"
  FileWrite $0 "}$\r$\n"
  FileClose $0
  
  ; Create empty download history file
  FileOpen $0 "$INSTDIR\gui_app\download_history.json" w
  FileWrite $0 "{$\r$\n"
  FileWrite $0 "  $\"videos$\": {},$\r$\n"
  FileWrite $0 "  $\"last_updated$\": $\"2023-01-01T00:00:00.000000$\"$\r$\n"
  FileWrite $0 "}$\r$\n"
  FileClose $0
  
  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\YouTube Playlist Downloader"
  CreateShortcut "$SMPROGRAMS\YouTube Playlist Downloader\YouTube Playlist Downloader.lnk" "$INSTDIR\YouTubePlaylistDownloader.exe"
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\YouTube Playlist Downloader.lnk" "$INSTDIR\YouTubePlaylistDownloader.exe"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add uninstall information to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\YouTubePlaylistDownloader" "DisplayName" "YouTube Playlist Downloader"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\YouTubePlaylistDownloader" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\YouTubePlaylistDownloader" "DisplayIcon" "$INSTDIR\YouTubePlaylistDownloader.exe"
SectionEnd

; Uninstall section
Section "Uninstall"
  ; Remove Start Menu shortcut
  Delete "$SMPROGRAMS\YouTube Playlist Downloader\YouTube Playlist Downloader.lnk"
  RMDir "$SMPROGRAMS\YouTube Playlist Downloader"
  
  ; Remove Desktop shortcut
  Delete "$DESKTOP\YouTube Playlist Downloader.lnk"
  
  ; Remove installed files
  Delete "$INSTDIR\YouTubePlaylistDownloader.exe"
  Delete "$INSTDIR\config.ini"
  Delete "$INSTDIR\app.log"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$INSTDIR\gui_app\playlists.json"
  Delete "$INSTDIR\gui_app\download_history.json"
  
  ; Remove directories if empty
  RMDir "$INSTDIR\data\audio"
  RMDir "$INSTDIR\data"
  RMDir "$INSTDIR\gui_app"
  RMDir "$INSTDIR"
  
  ; Remove uninstall information
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\YouTubePlaylistDownloader"
SectionEnd