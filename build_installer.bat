@echo off
chcp 65001 >nul
title RAIN Installer Build
echo ========================================
echo   RAIN Desktop - NSIS Installer Build
echo ========================================
echo.
echo Building RAIN_Setup.exe...
echo.
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
echo.
echo ========================================
if exist "RAIN_Setup.exe" (
    echo   Done! RAIN_Setup.exe
    for %%A in ("RAIN_Setup.exe") do echo   Size: %%~zA bytes
) else (
    echo   [ERROR] Build failed
)
echo ========================================
pause
