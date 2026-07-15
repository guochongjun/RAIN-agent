@echo off
chcp 65001 >nul
echo Checking Python environment...
echo.

REM Get Python path from registry or common locations
set PYTHON=
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Python\PythonCore\3.11\InstallPath" /ve 2^>nul') do set PYTHON=%%b
if not defined PYTHON set PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\
if not defined PYTHON set PYTHON=C:\Python311\

set PYTHON_EXE=%PYTHON%python.exe
set PIP_EXE=%PYTHON%Scripts\pip.exe

if not exist "%PYTHON_EXE%" (
    echo Python not found at %PYTHON_EXE%
    echo Trying default...
    set PYTHON_EXE=python
    set PIP_EXE=pip
)

echo Python: %PYTHON_EXE%
%PYTHON_EXE% --version
echo.

echo Checking PyQt5...
%PYTHON_EXE% -c "import PyQt5; print('PyQt5:', PyQt5.QtCore.PYQT_VERSION_STR)" 2>&1
if %errorlevel% neq 0 (
    echo PyQt5 NOT installed. Installing...
    %PIP_EXE% install PyQt5 openai pyinstaller
)

echo.
echo Checking openai...
%PYTHON_EXE% -c "import openai; print('openai:', openai.__version__)" 2>&1

echo.
echo All checks complete.
pause
