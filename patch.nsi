; RAIN Patch - Hermes-agent modules
!include "MUI2.nsh"

Name "RAIN Patch"
OutFile "RAIN_Patch.exe"
Unicode True
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\RAIN"
SetCompressor lzma
CRCCheck off

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"

Section "Patch"
    nsExec::ExecToLog 'taskkill /f /im RAIN.exe 2>nul'

    SetOutPath "$INSTDIR\tools"
    File "vendor\tools\7z.exe"

    SetOutPath "$INSTDIR"
    File "dist\hermes-agent.7z"
    nsExec::ExecToLog '"$INSTDIR\tools\7z.exe" x "$INSTDIR\hermes-agent.7z" -o"$INSTDIR" -y -aoa'
    Delete "$INSTDIR\hermes-agent.7z"

    MessageBox MB_OK "RAIN engine modules patched."
SectionEnd
