@echo off
python -c "import PyQt5; print('PyQt5:', PyQt5.QtCore.PYQT_VERSION_STR)"
python -c "import openai; print('openai:', openai.__version__)"
python -c "import sys; sys.path.insert(0, '.'); import RAIN_desktop; print('RAIN_desktop: OK')"
pause
