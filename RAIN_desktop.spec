# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for RAIN Desktop — full hermes-agent engine + common Python libs.
"""
import sys
from pathlib import Path

_SPEC_DIR = Path(SPECPATH) if 'SPECPATH' in dir() else Path.cwd()
HERMES_ROOT = _SPEC_DIR.parent

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# ── Collect ALL submodules from hermes-agent packages ──
PACKAGES = [
    'agent', 'tools', 'providers', 'gateway', 'plugins',
    'hermes_cli', 'acp_adapter', 'tui_gateway', 'cron', 'apps',
]
ALL_IMPORTS = []
for pkg in PACKAGES:
    try:
        subs = collect_submodules(pkg)
        ALL_IMPORTS.extend(subs)
    except Exception:
        pass

# ── Collect data files (non-Python assets) ──
DATAS = [
    (str(HERMES_ROOT / 'skills'), 'skills'),
    (str(HERMES_ROOT / 'optional-skills'), 'optional-skills'),
    (str(HERMES_ROOT / 'locales'), 'locales'),
    (str(HERMES_ROOT / 'assets'), 'assets'),
    (str(HERMES_ROOT / 'tools' / 'neutts_samples'), 'tools/neutts_samples'),
]
for plugin_dir in (HERMES_ROOT / 'plugins').iterdir():
    if plugin_dir.is_dir() and plugin_dir.name != '__pycache__':
        try:
            plugin_datas = collect_data_files(
                f'plugins.{plugin_dir.name}',
                include_py_files=False,
            )
            DATAS.extend(plugin_datas)
        except Exception:
            pass

# ── Explicit hidden imports ──
EXPLICIT = [
    # Core deps
    'openai', 'httpx', 'yaml', 'rich', 'jinja2', 'pydantic',
    'tenacity', 'dotenv', 'certifi', 'requests', 'croniter',
    'packaging', 'concurrent_log_handler',
    'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
    # Hermes core
    'hermes_bootstrap', 'hermes_constants', 'hermes_logging',
    'hermes_state', 'hermes_time', 'utils',
    'run_agent', 'model_tools', 'toolsets', 'toolset_distributions',
    # ── Common Python libraries for AI use ──
    'pandas', 'numpy', 'scipy',
    'matplotlib', 'PIL',
    'sklearn',
    'lxml', 'bs4',
    'jieba',
    'cryptography', 'bcrypt',
    'psutil', 'sqlalchemy',
    'colorama', 'wcwidth',
    'cffi', 'pycparser',
    'aiofiles', 'watchfiles', 'websockets',
    'multiprocessing',
    # Document / spreadsheet
    'openpyxl', 'xlsxwriter', 'xlrd',
    'docx',
    'PyPDF2', 'pdfplumber', 'reportlab',
    # Image / data
    'imageio',
    'tqdm',
    'pydub',
    # ── Web automation / scraping ──
    'selenium', 'webdriver_manager',
    'flask',
    'websocket',
    'trio', 'trio_websocket',
    'wsproto',
]

# ── Only exclude truly heavy / specialized packages ──
EXCLUDES = [
    'tkinter',
    'tensorflow', 'torch', 'torchvision', 'torchaudio', 'transformers',
    'onnxruntime',
    'av',
    'gradio', 'gradio_client',
    'IPython', 'jupyter', 'notebook', 'nbformat', 'nbconvert',
    'uvicorn', 'starlette', 'fastapi',
    'pytest',
    'win32com', 'pywintypes', 'pythoncom',
]

a = Analysis(
    ['RAIN_desktop.py'],
    pathex=[str(HERMES_ROOT)],
    binaries=[],
    datas=DATAS,
    hiddenimports=ALL_IMPORTS + EXPLICIT,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RAIN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
