; RAIN Desktop + Portable Tools - NSIS Installer
; Unicode NSIS required (nsis-3.0+)

!include "MUI2.nsh"
!include "FileFunc.nsh"

; -- General --------------------------------------------------
Name "RAIN Desktop"
OutFile "RAIN_Setup.exe"
Unicode True
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\RAIN"
SetCompressor lzma
CRCCheck off

!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; -- Pages ----------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "SimpChinese"

; -- Installer Section ----------------------------------------
Section "Install"
    SetOutPath "$INSTDIR"

    ; Main launcher + script
    File "dist\RAIN.exe"
    File "RAIN_desktop.py"

    ; 7z extractor (placed in tools)
    SetOutPath "$INSTDIR\tools"
    File "vendor\tools\7z.exe"
    File "vendor\tools\jq.exe"

    ; Git Bash
    SetOutPath "$INSTDIR\gitbash"
    File /r "vendor\gitbash\*"

    ; FFmpeg
    SetOutPath "$INSTDIR\ffmpeg"
    File /r "vendor\ffmpeg\*"

    ; Python (7z archive -> extract)
    SetOutPath "$INSTDIR"
    File "dist\python.7z"
    nsExec::ExecToLog '"$INSTDIR\tools\7z.exe" x "$INSTDIR\python.7z" -o"$INSTDIR" -y -mmt=on'
    Delete "$INSTDIR\python.7z"

    SetOutPath "$INSTDIR"

    ; Shortcuts
    CreateDirectory "$SMPROGRAMS\RAIN"
    CreateShortCut "$SMPROGRAMS\RAIN\RAIN.lnk" "$INSTDIR\RAIN.exe"
    CreateShortCut "$DESKTOP\RAIN.lnk" "$INSTDIR\RAIN.exe"
    CreateShortCut "$SMPROGRAMS\RAIN\Uninstall RAIN.lnk" "$INSTDIR\uninstall.exe"

    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Register in Add/Remove Programs
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "DisplayName" "RAIN Desktop"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "DisplayIcon" "$INSTDIR\RAIN.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "Publisher" "Jiangxi Panto Intelligence"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "DisplayVersion" "1.0.0"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "NoRepair" 1
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN" \
        "EstimatedSize" "$0"

SectionEnd

; -- Uninstaller Section --------------------------------------
Section "Uninstall"
    ; Remove shortcuts
    Delete "$DESKTOP\RAIN.lnk"
    Delete "$SMPROGRAMS\RAIN\RAIN.lnk"
    Delete "$SMPROGRAMS\RAIN\Uninstall RAIN.lnk"
    RMDir "$SMPROGRAMS\RAIN"

    ; Remove all files
    RMDir /r "$INSTDIR"

    ; Remove registry
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RAIN"

SectionEnd
