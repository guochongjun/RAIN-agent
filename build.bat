@echo off
chcp 65001 >nul
title RAIN Desktop - Build
echo.
echo ========================================
echo   RAIN Desktop - Build
echo ========================================
echo.
echo [1/2] Building launcher EXE...
pyinstaller --onefile --console --name RAIN rain_launcher.py --noconfirm --clean 2>&1
if %errorlevel% neq 0 (echo [ERROR] Build failed & pause & exit /b 1)
echo.
echo [2/2] Done!
echo ========================================
echo   dist\RAIN.exe (launcher)
echo ========================================
echo.
echo To build installer, run: build_installer.bat
pause
