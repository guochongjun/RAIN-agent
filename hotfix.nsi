; RAIN Desktop - Incremental Hotfix
Unicode True
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\RAIN"
SetCompressor lzma
CRCCheck off
Name "RAIN Hotfix"
OutFile "RAIN_Hotfix_Update.exe"

Section "Install"
    IfFileExists "$INSTDIR\RAIN.exe" 0 not_installed
    SetOutPath "$INSTDIR"
    File "RAIN_desktop.py"
    IfFileExists "$INSTDIR\vendor\*" 0 done_vendor
    SetOutPath "$INSTDIR\vendor"
    File "/oname=RAIN_desktop.py" "RAIN_desktop.py"
    done_vendor:
    RMDir /r "$INSTDIR\__pycache__"
    RMDir /r "$INSTDIR\vendor\__pycache__"
    RMDir /r "$INSTDIR\agent\__pycache__"
    MessageBox MB_ICONINFORMATION|MB_OK "Update OK. Restart RAIN."
    Goto done
    not_installed:
    MessageBox MB_ICONSTOP|MB_OK "RAIN not installed."
    done:
SectionEnd
