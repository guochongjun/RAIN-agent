; RAIN Update - All fixes
!include "MUI2.nsh"

Name "RAIN Update"
OutFile "RAIN_Update.exe"
Unicode True
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\RAIN"
SetCompressor lzma
CRCCheck off

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"

Section "Update"
    nsExec::ExecToLog 'taskkill /f /im RAIN.exe 2>nul'

    ; Tools
    SetOutPath "$INSTDIR\tools"
    File "vendor\tools\7z.exe"

    ; RAIN_desktop.py
    SetOutPath "$INSTDIR"
    File "RAIN_desktop.py"

    ; Hermes-agent source
    File "dist\hermes-agent.7z"
    RMDir /r "$INSTDIR\hermes-agent"
    nsExec::ExecToLog '"$INSTDIR\tools\7z.exe" x "$INSTDIR\hermes-agent.7z" -o"$INSTDIR" -y'
    Delete "$INSTDIR\hermes-agent.7z"

    ; Python (with PyQt5 bindings + _ctypes fix)
    File "dist\python.7z"
    RMDir /r "$INSTDIR\python"
    nsExec::ExecToLog '"$INSTDIR\tools\7z.exe" x "$INSTDIR\python.7z" -o"$INSTDIR" -y -mmt=on'
    Delete "$INSTDIR\python.7z"

    ; Launcher
    File "dist\RAIN.exe"

    MessageBox MB_OK "RAIN update complete!"
SectionEnd
