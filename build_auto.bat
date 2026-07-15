@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title RAIN Desktop - Auto Build

echo.
echo ========================================
echo   RAIN Desktop - Auto Build
echo ========================================
echo.

:: Check Python
echo [1/4] Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    exit /b 1
)
python --version
echo.

:: Install deps
echo [2/4] Installing dependencies...
pip install PyQt5 openai pyinstaller --quiet 2>nul
echo Done.
echo.

:: Build EXE
echo [3/4] Building EXE...
pyinstaller RAIN_desktop.spec --noconfirm --clean 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    exit /b 1
)
echo.

:: Copy Git Bash
echo [4/5] Copying Git Bash...
if exist "vendor\gitbash\" (
    robocopy "vendor\gitbash" "dist\gitbash" /E /NFL /NDL /NJH /NJS /MT:8 >nul
    echo Done.
) else (
    echo [SKIP] vendor\gitbash not found
)
echo.
:: Result
echo [5/5] Done!
echo.
echo ========================================
echo   EXE: dist\RAIN.exe
echo   Git: dist\gitbash\
echo ========================================
echo.
exit /b 0
