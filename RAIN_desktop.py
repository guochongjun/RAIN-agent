#!/usr/bin/env python3
"""
RAIN Desktop — Windows AI Assistant
Integrates the RAIN agent engine with PyQt5 GUI.
"""
import sys
import os
import io
import traceback
import datetime
from pathlib import Path

# ── Portable Python path injection ─────────────────────────
_PYTHON_HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python")
if os.path.isdir(_PYTHON_HOME):
    # Delete _pth file — it forces isolated mode and blocks normal imports
    _pth_file = os.path.join(_PYTHON_HOME, "python311._pth")
    if os.path.isfile(_pth_file):
        os.remove(_pth_file)
    os.environ["PYTHONHOME"] = _PYTHON_HOME
    sys.path.insert(0, os.path.join(_PYTHON_HOME, "Lib", "site-packages"))
    sys.path.insert(0, os.path.join(_PYTHON_HOME, "Lib"))
    sys.path.insert(0, os.path.join(_PYTHON_HOME, "DLLs"))
    _dlls = os.path.join(_PYTHON_HOME, "DLLs")
    if os.path.isdir(_dlls):
        os.environ["PATH"] = _PYTHON_HOME + os.pathsep + _dlls + os.pathsep + os.environ.get("PATH", "")
        os.add_dll_directory(_PYTHON_HOME)
        try:
            os.add_dll_directory(_dlls)
        except Exception:
            pass
# Fix: windowed PyInstaller has no console → stdout/stderr are None
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

def _global_excepthook(exc_type, exc_val, exc_tb):
    tb_text = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "RAIN - 崩溃", f"程序遇到错误:\n\n{str(exc_val)}")
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_val, exc_tb)

sys.excepthook = _global_excepthook

import json
import re
import tempfile
import threading
import time
import traceback
from pathlib import Path

# ── Inject RAIN agent source path ─────────────────────────
_HERMES_ROOT = Path(__file__).resolve().parent
if str(_HERMES_ROOT) not in sys.path:
    sys.path.insert(0, str(_HERMES_ROOT))

# ── Redirect Hermes data to RAIN directory ────────────────
_RAIN_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "RAIN"
os.environ["HERMES_HOME"] = str(_RAIN_DATA_DIR)

# ── Point to bundled Git Bash and Python ──────────────────
_BUNDLED_GIT_BASH = _RAIN_DATA_DIR / "gitbash" / "bin" / "bash.exe"
if _BUNDLED_GIT_BASH.is_file():
    os.environ["HERMES_GIT_BASH_PATH"] = str(_BUNDLED_GIT_BASH)

# PyInstaller bundles Python as sys.executable
if getattr(sys, 'frozen', False):
    _python_dir = str(Path(sys.executable).parent)
    if _python_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _python_dir + os.pathsep + os.environ.get("PATH", "")

# ── RAIN bootstrap (UTF-8 on Windows) ─────────────────────
try:
    import hermes_bootstrap  # noqa: F401
except ModuleNotFoundError:
    pass

# ── Qt ──────────────────────────────────────────────────────
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSplitter,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
    QMenuBar, QAction, QStatusBar, QFileDialog, QTabWidget,
    QListWidget, QListWidgetItem, QPlainTextEdit, QProgressBar,
    QComboBox, QCheckBox, QGroupBox, QScrollArea, QFrame,
    QGridLayout, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QSize
from PyQt5.QtGui import QFont, QTextCursor, QColor, QIcon, QPalette, QKeySequence

# ── RAIN agent engine ─────────────────────────────────────
try:
    from run_agent import AIAgent
    from hermes_state import SessionDB
    from hermes_constants import get_hermes_home
    from toolsets import get_toolset_names
    import providers as _providers
    HERMES_AVAILABLE = True
except ImportError as e:
    HERMES_AVAILABLE = False
    _hermes_import_error = str(e)

# ── Constants ───────────────────────────────────────────────
APP_NAME = "RAIN"
APP_VERSION = "2.0.0"
SETTINGS_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "RAIN"
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)  # ensure dir exists before any file writes

# ── RAIN permission guard: auto-deny external file ops for ALL agents (incl. subagents) ──
os.environ["RAIN_PERM_GUARD"] = "1"

# ── Dark theme ──────────────────────────────────────────────
DARK_STYLE = """
QMainWindow, QDialog { background-color: #1e1e2e; color: #cdd6f4; }
QTextEdit, QPlainTextEdit, QLineEdit, QListWidget, QComboBox {
    background-color: #181825; color: #cdd6f4; border: 1px solid #313244;
    border-radius: 6px; padding: 8px; font-family: "Segoe UI","Microsoft YaHei",sans-serif; font-size: 13px;
}
QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus, QComboBox:focus { border: 1px solid #89b4fa; }
QPushButton {
    background-color: #45475a; color: #cdd6f4; border: none; border-radius: 6px;
    padding: 8px 16px; font-weight: bold; font-size: 12px;
}
QPushButton:hover { background-color: #585b70; }
QPushButton:pressed { background-color: #313244; }
QPushButton#sendBtn { background-color: #89b4fa; color: #1e1e2e; }
QPushButton#sendBtn:hover { background-color: #b4befe; }
QPushButton#stopBtn { background-color: #f38ba8; color: #1e1e2e; }
QPushButton#stopBtn:hover { background-color: #fab387; }
QLabel { color: #a6adc8; font-size: 12px; }
QStatusBar { background-color: #11111b; color: #a6adc8; }
QMenuBar { background-color: #11111b; color: #cdd6f4; }
QMenuBar::item:selected { background-color: #313244; }
QMenu { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; }
QMenu::item:selected { background-color: #45475a; }
QSplitter::handle { background-color: #313244; width: 2px; }
QTabWidget::pane { border: 1px solid #313244; background-color: #1e1e2e; }
QTabBar::tab { background-color: #181825; color: #a6adc8; padding: 6px 16px; border: 1px solid #313244; border-bottom: none; }
QTabBar::tab:selected { background-color: #1e1e2e; color: #89b4fa; }
QProgressBar { border: none; background-color: #313244; border-radius: 3px; height: 4px; }
QProgressBar::chunk { background-color: #89b4fa; border-radius: 3px; }
QGroupBox { border: 1px solid #313244; border-radius: 6px; margin-top: 8px; padding-top: 16px; color: #cdd6f4; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QCheckBox { color: #cdd6f4; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #45475a; border-radius: 3px; background: #181825; }
QCheckBox::indicator:checked { background: #89b4fa; border-color: #89b4fa; }
QSpinBox, QDoubleSpinBox {
    background-color: #181825; color: #cdd6f4; border: 1px solid #313244;
    border-radius: 4px; padding: 4px 8px;
}
QScrollArea { border: none; background: transparent; }
QComboBox { min-width: 120px; }
QComboBox QAbstractItemView {
    background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; selection-background-color: #45475a;
}
"""


# ── Settings Manager ────────────────────────────────────────
class Settings:
    DEFAULTS = {
        "provider": "openai",
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "system_prompt": "你好，我叫RAIN，由江西磐拓智能科技有限公司开发的一款智能AI助手。我的目标是在各类任务中为你提供高效、精准的帮助——无论是回答问题、编写代码、分析信息，还是执行具体操作。有什么可以帮你的？😊",
        "max_iterations": 25,
        "max_tokens": 4096,
        "temperature": 0.7,
        "auto_scroll": True,
        "window_x": 100, "window_y": 100,
        "window_w": 1100, "window_h": 750,
        "enabled_toolsets": "all",
        "workspace_dir": "",
        # Additional provider keys
        "openrouter_key": "",
        "deepseek_key": "",
        "dashscope_key": "",
        "google_key": "",
        "anthropic_key": "",
    }

    def __init__(self, username=""):
        self._username = username
        self._data = dict(self.DEFAULTS)
        self.load()

    def _file(self):
        d = SETTINGS_DIR / (self._username or "default")
        d.mkdir(parents=True, exist_ok=True)
        return d / "settings.json"

    def switch_user(self, username):
        """Switch to a different user's settings file."""
        self.save()
        self._username = username
        self._data = dict(self.DEFAULTS)
        self.load()

    def load(self):
        try:
            f = self._file()
            if f.exists():
                self._data.update(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass

    def save(self):
        try:
            self._file().write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            import traceback

    def get(self, key, default=None):
        return self._data.get(key, self.DEFAULTS.get(key, default))

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def all(self):
        return dict(self._data)


settings = Settings()


# ── Permission Checker ──────────────────────────────────────
class PermissionChecker:
    """Three-tier permission model:
    1. Inside workspace: ALL operations allowed, no auth
    2. Outside workspace, READ: allowed, no auth
    3. Outside workspace, WRITE/DELETE: require authorization

    Uses an event QUEUE so concurrent requests never lose track of
    which Event belongs to which operation.
    """
    def __init__(self, get_workspace):
        self._get_ws = get_workspace
        self._approve_all = set()        # paths approved for entire session
        self._lock = threading.Lock()    # serialize permission requests
        self._queue_lock = threading.Lock()
        self._pending = []               # list of (event, result_ref) tuples
        self._result = False
        self._current_tool = ""
        self._current_paths = ""
        self._current_op = ""
        self.request = None              # pyqtSignal(str, str)
        self.locked_down = False
        self._denied_count = 0           # how many times user denied in this request
        self._denied_paths = set()       # paths denied this request
        self._cycle_approved = False     # "此次同意" — approve all remaining in cycle

    def _resolve_ws(self):
        ws = self._get_ws()
        if not ws:
            ws = str(Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path.cwd())
        return ws

    def _normalize_path(self, p: str) -> str:
        """Normalize WSL/Cygwin paths to Windows format and return normalized absolute path.
        /c/Users/... → C:\\Users\\..., /mnt/c/... → C:\\..."""
        if not p:
            return p
        import re as _nre
        # /mnt/c/... (WSL default) → C:/...
        m = _nre.match(r'^/mnt/([a-zA-Z])(/.*)?$', p)
        if m:
            p = f'{m.group(1).upper()}:{m.group(2) or "/"}'
        # /c/... (Cygwin / Git Bash style, single letter after /) → C:/...
        m = _nre.match(r'^/([a-zA-Z])(/.*)?$', p)
        if m and not p.startswith('/mnt/') and not p.startswith('/proc/') and not p.startswith('/dev/'):
            # Only convert if it looks like a Windows drive mount, not a regular Unix path
            # Check: the matched letter should be a single letter followed by / or end
            if len(m.group(1)) == 1 and (m.group(2) or '').startswith('/'):
                p = f'{m.group(1).upper()}:{m.group(2) or "/"}'
                return os.path.normpath(p)
        # Regular path — use normpath for consistency
        return os.path.normpath(p)

    def _is_subpath(self, child: str, parent: str) -> bool:
        """Check if child path is inside parent path (case-insensitive, robust)."""
        if not child or not parent:
            return False
        try:
            child_r = os.path.normpath(os.path.abspath(self._normalize_path(str(child))))
            parent_r = os.path.normpath(os.path.abspath(self._normalize_path(str(parent))))
            cl = child_r.lower().rstrip(os.sep)
            pl = parent_r.lower().rstrip(os.sep)
            return cl == pl or cl.startswith(pl + os.sep)
        except Exception:
            return False

    def check_read(self, tool_name, *paths):
        """Read operations: always allowed (even outside workspace)."""
        if self.locked_down:
            return False
        return True  # Read is always permitted

    def is_inside_workspace(self, path):
        """Check if a path is inside the workspace. Normalizes WSL paths."""
        if not path:
            return True
        ws = self._resolve_ws()
        if not ws:
            return True
        return self._is_subpath(str(path), ws)

    def check_write(self, tool_name, *paths):
        """Write/delete operations: workspace=allowed, external=auth required."""
        if self.locked_down:
            return False
        # Cycle-level: user already approved "此次同意" — allow all
        if self._cycle_approved:
            return True
        # Cycle-level: user already denied — block all
        if self._denied_count > 0:
            return False

        ws = self._resolve_ws()
        tmp = tempfile.gettempdir()
        hh = os.environ.get("HERMES_HOME", "")

        outside = []
        for p in paths:
            if not p:
                continue
            sp = str(p)
            # Non-path tokens (no separator / drive) → always external, show dialog
            if not re.search(r'[\\\\/:]|[A-Za-z]:', sp):
                if sp not in self._approve_all:
                    outside.append(sp)
                continue
            if self._is_subpath(sp, ws) or self._is_subpath(sp, tmp):
                continue
            if hh and self._is_subpath(sp, hh):
                continue
            if sp not in self._approve_all:
                outside.append(sp)

        if outside:
            # External paths detected — show confirmation dialog
            result = [False]  # mutable container so grant/deny can mutate
            event = threading.Event()
            with self._queue_lock:
                self._pending.append((event, result))

            with self._lock:
                self._current_tool = tool_name
                self._current_op = "write"
                self._current_paths = "\n".join(outside)
                if self.request:
                    self.request.emit(tool_name, self._current_paths)
            event.wait(timeout=60)
            return result[0]
        return True

    def _pop_pending(self):
        """Pop the oldest pending request. Returns (event, result) or (None, None)."""
        with self._queue_lock:
            if self._pending:
                return self._pending.pop(0)
            return None, None

    def grant(self, approve_all=False):
        os.environ.pop("RAIN_DENIED", None)  # clear deny signal
        if approve_all:
            for p in self._current_paths.split("\n"):
                self._approve_all.add(p)
        else:
            # "此次同意" — approve all remaining operations in this cycle
            self._cycle_approved = True
        event, result = self._pop_pending()
        if result is not None:
            result[0] = True
            event.set()

    def deny(self):
        self._denied_count += 1
        os.environ["RAIN_DENIED"] = "1"  # signal sub-processes
        if self._current_paths:
            for p in self._current_paths.split("\n"):
                self._denied_paths.add(p)
        event, result = self._pop_pending()
        if result is not None:
            result[0] = False
            event.set()

    def deny_all(self):
        """Deny all future operations — hard stop."""
        self.locked_down = True
        self._denied_count += 1
        os.environ["RAIN_DENIED"] = "1"  # signal sub-processes
        if self._current_paths:
            for p in self._current_paths.split("\n"):
                self._denied_paths.add(p)
        event, result = self._pop_pending()
        if result is not None:
            result[0] = False
            event.set()

    def reset(self):
        self._approve_all.clear()
        self.locked_down = False
        self._denied_count = 0
        self._denied_paths.clear()
        self._cycle_approved = False
        os.environ.pop("RAIN_DENIED", None)  # clear sub-process deny signal
        with self._queue_lock:
            # Drain any pending requests
            for event, result in self._pending:
                result[0] = False
                event.set()
            self._pending.clear()

# Module-level instance (patched after login)
perm_checker = PermissionChecker(lambda: settings.get("workspace_dir", ""))

# ── File System Watcher ─────────────────────────────────────
class FileSystemGuard(QThread):
    """Monitors non-workspace directories for file modifications in real-time."""
    alert = pyqtSignal(str, str)  # (action, path)

    def __init__(self, get_workspace):
        super().__init__()
        self._get_ws = get_workspace
        self._stop = threading.Event()
        self._watch_paths = []
        self._init_watch_paths()

    def _init_watch_paths(self):
        """Set up directories to monitor: Desktop, Documents, Downloads, etc."""
        base = os.environ.get("USERPROFILE", "")
        if base:
            candidates = [
                os.path.join(base, "Desktop"),
                os.path.join(base, "Documents"),
                os.path.join(base, "Downloads"),
                os.path.join(base, "Pictures"),
            ]
            for p in candidates:
                if os.path.isdir(p):
                    self._watch_paths.append(p)

    def run(self):
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            return  # watchdog not installed

        ws_r = None
        
        class GuardHandler(FileSystemEventHandler):
            def __init__(self, guard):
                self.guard = guard

            def _is_outside_ws(self, path):
                nonlocal ws_r
                if ws_r is None:
                    try:
                        ws_r = Path(self.guard._get_ws()).resolve()
                    except Exception:
                        ws_r = Path("__nonexistent__")
                try:
                    Path(path).resolve().relative_to(ws_r)
                    return False
                except (ValueError, OSError):
                    return True

            def on_modified(self, event):
                if not event.is_directory and self._is_outside_ws(event.src_path):
                    self.guard.alert.emit("修改", event.src_path)

            def on_created(self, event):
                if not event.is_directory and self._is_outside_ws(event.src_path):
                    self.guard.alert.emit("创建", event.src_path)

            def on_deleted(self, event):
                if not event.is_directory and self._is_outside_ws(event.src_path):
                    self.guard.alert.emit("删除", event.src_path)

            def on_moved(self, event):
                if not event.is_directory and self._is_outside_ws(event.dest_path):
                    self.guard.alert.emit("移动", f"{event.src_path} → {event.dest_path}")

        observer = Observer()
        handler = GuardHandler(self)
        for p in self._watch_paths:
            if os.path.isdir(p):
                try:
                    observer.schedule(handler, p, recursive=True)
                except Exception:
                    pass

        observer.start()
        try:
            while not self._stop.wait(5):
                pass
        finally:
            observer.stop()
            observer.join()

    def stop_watching(self):
        self._stop.set()

fs_guard = FileSystemGuard(lambda: settings.get("workspace_dir", ""))

# ── Agent Worker Thread ─────────────────────────────────────
class RAINWorker(QThread):
    """Runs the full RAIN AIAgent in a background thread."""
    response_chunk = pyqtSignal(str)       # streaming text
    thinking = pyqtSignal(str)             # thinking/reasoning
    tool_start = pyqtSignal(str, str)      # name, args_json
    tool_complete = pyqtSignal(str, str)   # name, result
    tool_progress = pyqtSignal(str, str)   # name, status
    status_msg = pyqtSignal(str)           # status bar
    notice = pyqtSignal(str)               # notices
    finished = pyqtSignal(str, dict)       # final_response, metadata
    error = pyqtSignal(str)
    perm_request = pyqtSignal(str, str)    # (tool_name, paths_desc) for permission dialog

    def __init__(self, message, history=None, provider_config=None):
        super().__init__()
        self.message = message
        self.history = history or []
        self.provider_config = provider_config or {}
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        if not HERMES_AVAILABLE:
            self.error.emit(f"RAIN引擎不可用: {_hermes_import_error}")
            return

        try:
            # ── Switch to workspace directory ──
            ws = settings.get("workspace_dir", "")
            if ws and os.path.isdir(ws):
                os.chdir(ws)
                self.status_msg.emit(f"工作目录: {ws}（内部操作无需授权）")
            else:
                import sys as _sys
                ws = str(Path(_sys.executable).parent if getattr(_sys, 'frozen', False) else Path.cwd())
                self.status_msg.emit(f"工作目录(默认): {ws}（内部操作无需授权）")

            # ── Patch tools with permission checks ──
            if HERMES_AVAILABLE:
                try:
                    import tools.file_tools as _ft
                    import tools.terminal_tool as _tt
                    import tools.browser_tool as _bt
                    from tools.registry import registry
                    
                    # Restore original dispatch to prevent chain-wrapping across workers
                    global _ORIGINAL_DISPATCH
                    if '_ORIGINAL_DISPATCH' not in globals():
                        _ORIGINAL_DISPATCH = registry.dispatch
                    else:
                        registry.dispatch = _ORIGINAL_DISPATCH
                    _orig_dispatch = _ORIGINAL_DISPATCH

                    def _guarded_dispatch(name, args, **kw):
                        """Intercept write/delete ops — show dialog for external paths."""
                        self.status_msg.emit(f"🔍 权限检查: {name}")
                        if os.environ.get("RAIN_DENIED") == "1":
                            raise PermissionError("权限被拒绝：用户已拒绝外部文件操作")
                        if perm_checker.locked_down:
                            raise PermissionError("权限被拒绝：用户已停止所有操作")

                        # ── Universal path scan: check ALL args for any Windows absolute paths ──
                        import re as _ure
                        _ABS_PATH_RE = re.compile(r'[A-Za-z]:[\\/][^\s"\x27&|;<>]+')
                        def _scan_paths(obj, depth=0):
                            """Recursively scan args for Windows absolute paths."""
                            if depth > 5:
                                return []
                            if isinstance(obj, str):
                                return _ABS_PATH_RE.findall(obj)
                            if isinstance(obj, dict):
                                result = []
                                for v in obj.values():
                                    result.extend(_scan_paths(v, depth + 1))
                                return result
                            if isinstance(obj, (list, tuple)):
                                result = []
                                for v in obj:
                                    result.extend(_scan_paths(v, depth + 1))
                                return result
                            return []
                        all_paths = _scan_paths(args)
                        outside_paths = [p for p in all_paths
                                        if not perm_checker.is_inside_workspace(p)
                                        and p not in perm_checker._approve_all]
                        if outside_paths and not perm_checker._cycle_approved:
                            if not perm_checker.check_write(name, *outside_paths):
                                raise PermissionError("权限被拒绝：参数含工作目录外的文件路径")

                        # ── write_file ──
                        if name == "write_file":
                            path = args.get("path", "")
                            if path:
                                # Detect operation type: create (new), delete (empty content), or overwrite
                                content = args.get("content", None)
                                if content is not None and content == "":
                                    op_type = "删除"
                                elif not os.path.exists(str(path)):
                                    op_type = "创建"
                                else:
                                    op_type = "修改/写入"
                                if not perm_checker.check_write(op_type + " " + name, path):
                                    raise PermissionError(f"权限被拒绝：不允许在工作目录外{op_type}文件")

                        # ── patch ──
                        elif name == "patch":
                            path = args.get("path", "")
                            new_str = args.get("new_string", "")
                            if path:
                                op_type = "删除内容" if (new_str == "") else "修改"
                                if not perm_checker.check_write(op_type + " " + name, path):
                                    raise PermissionError(f"权限被拒绝：不允许在工作目录外{op_type}文件")

                        # ── terminal ──
                        elif name == "terminal":
                            cmd = args.get("command", "")
                            wd = args.get("workdir", "")
                            paths = []
                            effective_wd = wd if wd else os.getcwd()
                            if wd:
                                paths.append(wd)
                            if cmd:
                                import re as _re
                                _WRITE_RE = re.compile(
                                    r'\b(?:del|erase|rd|rmdir|rm\s+-rf?|rm\b\s|move|ren|rename|'
                                    r'copy|xcopy|robocopy|mv\b\s|cp\b\s|scp|attrib|'
                                    r'icacls|cacls|takeown|reg\s+(?:add|delete|import|export)|'
                                    r'format|diskpart|chkdsk\s+/f|[^>]>[^>]|>>'
                                    r'|cd\s+|chdir\s+|pushd\s+|python\s+-c|cmd\s+/c|powershell|'
                                    r'Remove-Item|New-Item|Set-Content|Add-Content|Out-File|'
                                    r'Move-Item|Copy-Item|Rename-Item|Clear-Content)\b', re.I)
                                is_danger = bool(_WRITE_RE.search(cmd))
                                # Extract paths: quoted first (handles spaces), then unquoted
                                abs_paths = []
                                abs_paths += re.findall(
                                    r'''["']([A-Za-z]:[\\/][^"']+?)["']''', cmd
                                )
                                abs_paths += re.findall(
                                    r'(?<!["\x27])([A-Za-z]:[\\/][^\s"\x27&|;<>]+)', cmd
                                )
                                paths.extend(p.strip('"\'') for p in abs_paths)
                                if is_danger and not abs_paths:
                                    if effective_wd not in paths:
                                        paths.append(effective_wd)
                                # Always check external paths — even if cmd doesn't match danger patterns
                                elif not is_danger and abs_paths:
                                    pass  # paths already populated, will be checked below
                            if paths and not perm_checker.check_write(name, *paths):
                                raise PermissionError("权限被拒绝：命令涉及工作目录外的文件")

                        # ── execute_code ──
                        elif name == "execute_code":
                            code = args.get("code", "")
                            if code:
                                import re as _re2
                                _DESTROY = re.compile(
                                    r'(?:write_file|patch|open\s*\(|mkdir|makedirs|remove|'
                                    r'rmdir|unlink|rmtree|os\.remove|os\.rmdir|os\.unlink|'
                                    r'os\.rename|os\.chdir|chdir|shutil\.(?:rmtree|move|copy2?|copytree)|'
                                    r'pathlib\.Path|Path\s*\(|'
                                    r'to_excel|to_csv|to_json|to_parquet|to_feather|to_pickle|'
                                    r'\.dump\(|pickle\.dump|json\.dump|'
                                    r'csv\.writer|openpyxl|xlwt|xlsxwriter|'
                                    r'PIL\.Image\.save|\.save\(|cv2\.imwrite|'
                                    r'plt\.savefig|f\.write|\.write\('
                                    r'|Path\.home\(\)|os\.path\.expanduser|os\.environ|USERPROFILE|~\w)')
                                if _DESTROY.search(code):
                                    # Extract actual absolute Windows paths from code (quoted + unquoted)
                                    abs_paths = []
                                    abs_paths += re.findall(
                                        r'[\"\x27]([A-Za-z]:[\\/][^\"\x27]+?)[\"\x27]', code
                                    )
                                    abs_paths += re.findall(
                                        r'(?<![\"\x27])([A-Za-z]:[\\/][^\s\"\x27&|;<>]+)', code
                                    )
                                    # Also detect home-dir references: always external
                                    _HOME_RE = re.compile(
                                        r'(?:Path\.home\(\)|os\.path\.expanduser|USERPROFILE|~\w|'
                                        r'os\.environ\[\s*[\"\']HOME[\"\']\s*\])'
                                    )
                                    has_home_ref = bool(_HOME_RE.search(code))
                                    if abs_paths:
                                        # Check extracted absolute paths
                                        if not perm_checker.check_write(name, *abs_paths):
                                            raise PermissionError("权限被拒绝：代码尝试操作工作目录外的文件")
                                    elif has_home_ref:
                                        # Home-dir = always external, show dialog
                                        if not perm_checker.check_write(name, "用户主目录(Desktop/Documents等)"):
                                            raise PermissionError("权限被拒绝：代码涉及主目录文件操作")
                                    else:
                                        # No absolute paths, check CWD
                                        cwd = os.getcwd()
                                        if not perm_checker.is_inside_workspace(cwd):
                                            if not perm_checker.check_write(name, cwd):
                                                raise PermissionError("权限被拒绝：当前目录不在工作目录内")

                        return _orig_dispatch(name, args, **kw)

                    # Mark dispatch as guarded so rain_perm_guard skips
                    _guarded_dispatch._rain_guarded = True
                    registry.dispatch = _guarded_dispatch

                    self.status_msg.emit('权限已注入调度器')


                    self.status_msg.emit('权限已生效: 工作目录内全权限，外部读允许，外部写需授权')
                except Exception as e:
                    import traceback
                    self.status_msg.emit(f'权限补丁失败: {e}')
                    self.error.emit(f'权限守卫安装失败: {e}\n{traceback.format_exc()[-300:]}')

            # ── Build the agent ──
            provider = settings.get("provider", "openai")
            cfg = self.provider_config
            # Diagnostic: where is agent module loaded from?
            try:
                import agent as _agent_mod
                import agent.agent_init as _ai_mod
            except Exception as _de:
                pass

            # Write SOUL.md with RAIN identity so it replaces DEFAULT_AGENT_IDENTITY
            # (load_soul_md reads from get_hermes_home() / "SOUL.md")
            _system_prompt = settings.get("system_prompt")
            if _system_prompt:
                try:
                    if HERMES_AVAILABLE:
                        _hermes_home = get_hermes_home()
                        _hermes_home.mkdir(parents=True, exist_ok=True)
                        (_hermes_home / "SOUL.md").write_text(_system_prompt, encoding="utf-8")
                except Exception as e:
                    pass

            try:
                agent = AIAgent(
                    base_url=cfg.get("base_url") or settings.get("base_url"),
                    api_key=cfg.get("api_key") or settings.get("api_key"),
                    provider=provider,
                    model=settings.get("model"),
                    max_iterations=settings.get("max_iterations", 25),
                    enabled_toolsets=_parse_toolsets(settings.get("enabled_toolsets", "all")),
                    quiet_mode=True,
                    skip_context_files=True,
                    load_soul_identity=True,
                    skip_memory=False,
                    ephemeral_system_prompt=settings.get("system_prompt"),
                    # Callbacks for UI integration
                    stream_delta_callback=lambda t: self.response_chunk.emit(t),
                    tool_start_callback=lambda n, a, **kw: self.tool_start.emit(n, json.dumps(a, ensure_ascii=False) if isinstance(a, dict) else str(a)),
                    tool_complete_callback=lambda n, r, **kw: self.tool_complete.emit(n, _safe_str(r)[:5000]),
                    tool_progress_callback=lambda n, s: self.tool_progress.emit(n, _safe_str(s)),
                    thinking_callback=lambda t: self.thinking.emit(t),
                    status_callback=lambda t: self.status_msg.emit(t),
                    notice_callback=lambda t: self.notice.emit(t),
                    step_callback=lambda info: self.status_msg.emit(f"Step {info.get('step','?')}"),
                )
            except Exception as init_exc:
                import traceback
                self.error.emit(f"引擎初始化失败: {init_exc}")
                return

            # ── Run conversation with RAIN system prompt ──
            # Appending workspace reminder so AI defaults to workspace directory
            _sysmsg = settings.get("system_prompt") or ""
            if ws:
                _sysmsg += f"\n\n【工作目录规则】你当前的工作目录是: {ws}。"
                _sysmsg += "所有文件操作(读、写、创建、搜索)默认在此目录中进行，除非用户明确指定了其他路径。"
                _sysmsg += "生成的临时代码、脚本、测试文件、下载内容等，也一律放在工作目录内。"
                _sysmsg += "用户说'创建文件'、'保存到桌面'等模糊指令时，优先使用工作目录，不要使用桌面或系统目录。"
            result = agent.run_conversation(
                self.message,
                system_message=_sysmsg,
            )
            self.finished.emit(result.get("final_response", "") or "", {})

        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"{e}\n\n{tb[-500:]}")


def _parse_toolsets(val):
    if not val or val == "all":
        return None  # AIAgent uses None to mean "all default toolsets"
    return [t.strip() for t in val.split(",") if t.strip()]


def _safe_str(obj):
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return str(obj)


# ── Login Dialog (Modern & Beautiful) ────────────────────────
class LoginDialog(QDialog):
    TAB_STYLE = (
        "QTabWidget::pane {"
        "  border: 1px solid #313244; border-radius: 10px;"
        "  background: #1a1a2e; padding: 8px;"
        "}"
        "QTabBar::tab {"
        "  background: #181825; color: #a6adc8;"
        "  padding: 10px 28px; border: 1px solid #313244;"
        "  border-bottom: none; border-radius: 8px 8px 0 0;"
        "  margin-right: 2px; font-size: 13px; font-weight: bold;"
        "}"
        "QTabBar::tab:selected {"
        "  background: #1a1a2e; color: #89b4fa;"
        "  border-bottom: 2px solid #89b4fa;"
        "}"
        "QTabBar::tab:hover { background: #313244; }"
    )

    INPUT_STYLE = (
        "QLineEdit {"
        "  padding: 10px 14px; border-radius: 8px; font-size: 13px;"
        "  background: #11111b; border: 1px solid #313244; color: #cdd6f4;"
        "}"
        "QLineEdit:focus { border: 1px solid #89b4fa; }"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RAIN - 登录")
        screen = QApplication.primaryScreen()
        ss = screen.availableSize()
        w = min(420, int(ss.width() * 0.35))
        h = min(400, int(ss.height() * 0.45))
        self.setMinimumSize(w, h)
        self.setStyleSheet(DARK_STYLE)
        self.username = ""

        main = QVBoxLayout(self)
        main.setSpacing(16)
        main.setContentsMargins(24, 20, 24, 20)

        # ── Logo / Title ──
        logo_area = QVBoxLayout()
        logo_area.setSpacing(4)
        logo = QLabel("RAIN")
        logo.setStyleSheet("font-size:32px;font-weight:900;color:#89b4fa;")
        logo.setAlignment(Qt.AlignCenter)
        logo_area.addWidget(logo)
        sub = QLabel("智能 AI 助手")
        sub.setStyleSheet("font-size:13px;color:#6c7086;")
        sub.setAlignment(Qt.AlignCenter)
        logo_area.addWidget(sub)
        main.addLayout(logo_area)

        # ── Tab panels ──
        self.stack = QTabWidget()
        self.stack.setStyleSheet(self.TAB_STYLE)

        # Login tab
        lt = QWidget()
        ltl = QVBoxLayout(lt)
        ltl.setSpacing(12)
        ltl.setContentsMargins(16, 20, 16, 16)

        self.login_user = QLineEdit()
        self.login_user.setPlaceholderText("👤  用户名")
        self.login_user.setStyleSheet(self.INPUT_STYLE)
        ltl.addWidget(self.login_user)

        self.login_pass = QLineEdit()
        self.login_pass.setEchoMode(QLineEdit.Password)
        self.login_pass.setPlaceholderText("🔒  密码")
        self.login_pass.setStyleSheet(self.INPUT_STYLE)
        self.login_pass.returnPressed.connect(self._do_login)
        ltl.addWidget(self.login_pass)

        self.remember_check = QCheckBox("记住我，下次自动登录")
        self.remember_check.setChecked(True)
        self.remember_check.setStyleSheet(
            "QCheckBox{color:#a6adc8;font-size:12px;spacing:8px;}"
            "QCheckBox::indicator{width:16px;height:16px;border:1px solid #45475a;border-radius:3px;background:#181825;}"
            "QCheckBox::indicator:checked{background:#89b4fa;border-color:#89b4fa;}")
        ltl.addWidget(self.remember_check)
        ltl.addStretch()

        self.stack.addTab(lt, "  登  录  ")

        # Register tab
        rt = QWidget()
        rtl = QVBoxLayout(rt)
        rtl.setSpacing(12)
        rtl.setContentsMargins(16, 20, 16, 16)

        self.reg_user = QLineEdit()
        self.reg_user.setPlaceholderText("👤  设置用户名")
        self.reg_user.setStyleSheet(self.INPUT_STYLE)
        rtl.addWidget(self.reg_user)

        self.reg_pass = QLineEdit()
        self.reg_pass.setEchoMode(QLineEdit.Password)
        self.reg_pass.setPlaceholderText("🔒  设置密码")
        self.reg_pass.setStyleSheet(self.INPUT_STYLE)
        rtl.addWidget(self.reg_pass)

        self.reg_pass2 = QLineEdit()
        self.reg_pass2.setEchoMode(QLineEdit.Password)
        self.reg_pass2.setPlaceholderText("🔒  确认密码")
        self.reg_pass2.setStyleSheet(self.INPUT_STYLE)
        self.reg_pass2.returnPressed.connect(self._do_register)
        rtl.addWidget(self.reg_pass2)
        rtl.addStretch()

        self.stack.addTab(rt, "  注  册  ")

        main.addWidget(self.stack)

        # ── Message ──
        self.msg_label = QLabel("")
        self.msg_label.setStyleSheet("color:#f38ba8;font-size:12px;padding:4px;")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)
        main.addWidget(self.msg_label)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.login_btn = QPushButton("🚀  登  录")
        self.login_btn.setStyleSheet(
            "QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:10px;"
            "padding:12px 0;font-size:14px;font-weight:bold;}"
            "QPushButton:hover{background:#b4befe;}"
            "QPushButton:pressed{background:#74c7ec;}")
        self.login_btn.clicked.connect(self._do_login)
        btn_row.addWidget(self.login_btn)

        self.reg_btn = QPushButton("✨  注  册")
        self.reg_btn.setStyleSheet(
            "QPushButton{background:#a6e3a1;color:#1e1e2e;border-radius:10px;"
            "padding:12px 0;font-size:14px;font-weight:bold;}"
            "QPushButton:hover{background:#94e2d5;}"
            "QPushButton:pressed{background:#74c7ec;}")
        self.reg_btn.clicked.connect(self._do_register)
        self.reg_btn.hide()
        btn_row.addWidget(self.reg_btn)

        main.addLayout(btn_row)

        self.stack.currentChanged.connect(lambda i: self._toggle_btn(i))
        self._init_user_db()

    def _init_user_db(self):
        import sqlite3, hashlib
        dbp = SETTINGS_DIR / "users.db"
        self._udb = sqlite3.connect(str(dbp))
        self._udb.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, created_at TEXT
        )""")
        self._udb.commit()

    def _toggle_btn(self, idx):
        self.login_btn.setVisible(idx == 0)
        self.reg_btn.setVisible(idx == 1)
        self.msg_label.setText("")

    def _hash(self, pw):
        import hashlib
        return hashlib.sha256(f"RAIN_SALT_{pw}".encode()).hexdigest()

    def _do_login(self):
        u = self.login_user.text().strip()
        p = self.login_pass.text().strip()
        if not u or not p:
            self.msg_label.setText("⚠ 请输入用户名和密码")
            return
        row = self._udb.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
        if not row:
            self.msg_label.setText("⚠ 用户不存在，请先注册")
            return
        if row[0] != self._hash(p):
            self.msg_label.setText("⚠ 密码错误")
            return
        self.username = u
        remember_file = SETTINGS_DIR / "remember.json"
        if self.remember_check.isChecked():
            try:
                remember_file.write_text(json.dumps({
                    "user": u, "pass_hash": row[0]
                }), encoding="utf-8")
            except Exception:
                pass
        else:
            try:
                remember_file.unlink(missing_ok=True)
            except Exception:
                pass
        self.accept()

    def _do_register(self):
        u = self.reg_user.text().strip()
        p = self.reg_pass.text().strip()
        p2 = self.reg_pass2.text().strip()
        if not u or not p:
            self.msg_label.setText("⚠ 请填写完整信息")
            return
        if len(u) < 2:
            self.msg_label.setText("⚠ 用户名至少2个字符")
            return
        if len(p) < 4:
            self.msg_label.setText("⚠ 密码至少4个字符")
            return
        if p != p2:
            self.msg_label.setText("⚠ 两次密码不一致")
            return
        row = self._udb.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone()
        if row:
            self.msg_label.setText("⚠ 用户名已存在")
            return
        import datetime
        self._udb.execute("INSERT INTO users VALUES (?,?,?)",
            (u, self._hash(p), datetime.datetime.now().isoformat()))
        self._udb.commit()
        self.username = u
        remember_file = SETTINGS_DIR / "remember.json"
        try:
            remember_file.write_text(json.dumps({
                "user": u, "pass_hash": self._hash(p)
            }), encoding="utf-8")
        except Exception:
            pass
        self.accept()


# ── Individual Setting Panels (one per menu item) ────────────

class _SettingPanel(QDialog):
    """One small dialog per setting group — opened from the 设置 menu."""
    
    INPUT_STYLE = (
        "QLineEdit,QSpinBox,QDoubleSpinBox,QComboBox{"
        "padding:8px 12px;border-radius:6px;font-size:13px;"
        "background:#11111b;border:1px solid #313244;color:#cdd6f4;}"
        "QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus,QComboBox:focus{border:1px solid #89b4fa;}"
    )
    BTN_STYLE = (
        "QPushButton{background:#313244;color:#a6adc8;border-radius:8px;padding:9px 24px;font-size:13px;font-weight:bold;}"
        "QPushButton:hover{background:#45475a;color:#cdd6f4;}"
    )
    SAVE_STYLE = (
        "QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:8px;padding:9px 28px;font-size:13px;font-weight:bold;}"
        "QPushButton:hover{background:#b4befe;}"
    )

    def __init__(self, parent, title, icon, build_fn):
        super().__init__(parent)
        self.setWindowTitle(f"RAIN - {title}")
        self.setMinimumWidth(420)
        self.setStyleSheet(DARK_STYLE)
        main = QVBoxLayout(self)
        main.setSpacing(12)
        main.setContentsMargins(20, 16, 20, 14)

        header = QLabel(f"{icon}  {title}")
        header.setStyleSheet("font-size:16px;font-weight:bold;color:#89b4fa;padding:4px 0;")
        main.addWidget(header)

        self._fields = []  # list of (name, widget)
        build_fn(self)     # populate _fields

        # Apply input styling
        for _, w in self._fields:
            w.setStyleSheet(self.INPUT_STYLE)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(self.BTN_STYLE)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        save_btn = QPushButton("💾 保存")
        save_btn.setStyleSheet(self.SAVE_STYLE)
        save_btn.clicked.connect(self._save_and_accept)
        btn_row.addWidget(save_btn)
        main.addLayout(btn_row)

    def _save_and_accept(self):
        for name, w in self._fields:
            if isinstance(w, (QLineEdit,)):
                settings.set(name, w.text().strip())
            elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                settings.set(name, w.value())
            elif isinstance(w, QComboBox):
                settings.set(name, w.currentData())
            elif isinstance(w, QPlainTextEdit):
                settings.set(name, w.toPlainText().strip())
            elif isinstance(w, QCheckBox):
                settings.set(name, w.isChecked())
        self.accept()

    def add_field(self, label, widget, key):
        fl = self.layout()
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#a6adc8;font-size:12px;min-width:80px;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(lbl)
        row.addWidget(widget)
        # Insert before the button row (last 2 items)
        fl.insertLayout(fl.count() - 1, row)
        self._fields.append((key, widget))


# ── Individual setting panels (opened from menu) ──────────

class MainWindow(QMainWindow):
    def __init__(self, username=""):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {username}" if username else f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(700, 450)
        screen = QApplication.primaryScreen()
        ss = screen.availableSize()
        dw = max(800, int(ss.width() * 0.60))
        dh = max(600, int(ss.height() * 0.65))
        self.setMinimumSize(800, 600)
        self.resize(settings.get("window_w", dw), settings.get("window_h", dh))
        self.move(settings.get("window_x"), settings.get("window_y"))

        # ── DPI scale factor for responsive sizing ──
        _dpi = screen.logicalDotsPerInch()
        self._s = max(0.75, min(2.0, _dpi / 96.0))  # clamp to [0.75, 2.0]

        self.worker: RAINWorker = None
        self._response_buffer = ""
        self._assistant_block_started = False
        self._current_tool_block = ""
        self.current_sid = None
        self._heartbeat_count = 0

        # Heartbeat timer to confirm event loop is alive
        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._heartbeat)
        self._hb_timer.start(5000)

        self._build_ui()
        self._build_menu()
        self._build_statusbar()
        self._init_db()
        self._refresh_sessions()
        self._new_session()

        # Start file system guard for non-workspace monitoring
        fs_guard.alert.connect(self._on_fs_alert)
        fs_guard.start()

    def _on_fs_alert(self, action, path):
        """FileSystemGuard alert — if outside workspace, show permission dialog and block on deny."""
        ws = settings.get("workspace_dir", "")
        if ws and perm_checker._is_subpath(str(path), ws):
            return  # inside workspace, ignore
        # External file operation detected — show permission dialog
        self._append_system(f"🛡 监控: 检测到外部{action}操作\n{path}")
        if perm_checker.locked_down or perm_checker._denied_count > 0:
            return  # already locked/denied, no further dialogs
        msg = QMessageBox(self)
        msg.setWindowTitle("权限确认 - 文件监控")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"检测到<b>工作目录外</b>的文件操作：\n\n<pre>{action}: {path}</pre>")
        msg.setInformativeText("「本次登录同意」= 该路径以后免确认\n「不同意」= 拒绝并停止当前 AI 操作")
        btn_all = msg.addButton("本次登录同意", QMessageBox.YesRole)
        btn_deny = msg.addButton("不同意", QMessageBox.RejectRole)
        msg.setDefaultButton(btn_deny)
        msg.exec_()
        clicked = msg.clickedButton()
        if clicked == btn_all:
            perm_checker._approve_all.add(str(path))
            self._append_system(f"🔓 已授权该路径（本次登录不再询问）")
        else:
            perm_checker.deny_all()
            self._append_system("🚫 已强制停止所有操作")
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.terminate()
                self.worker.wait(1000)
            self._reset_ui()
            self.sb_label.setText("文件操作被拒绝 - 已停止")

    def _build_ui(self):
        s = self._s
        central = QWidget()
        self.setCentralWidget(central)
        ml = QHBoxLayout(central)
        ml.setContentsMargins(4, 4, 4, 4)
        ml.setSpacing(4)

        # ── Left sidebar ──
        left = QWidget()
        left.setFixedWidth(int(190 * s))
        left.setStyleSheet("QWidget{background:#11111b;border-radius:10px;}")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(int(8*s), int(10*s), int(8*s), int(10*s))
        ll.setSpacing(int(8*s))

        history_label = QLabel("  📋  对话历史")
        history_label.setStyleSheet(f"color:#89b4fa;font-size:{int(12*s)}px;font-weight:bold;padding:2px;")
        ll.addWidget(history_label)

        self.session_list = QListWidget()
        self.session_list.setStyleSheet(
            f"QListWidget{{background:#181825;border:1px solid #313244;border-radius:8px;"
            f"padding:{int(4*s)}px;font-size:{int(10*s)}px;color:#cdd6f4;outline:none;}}"
            f"QListWidget::item{{padding:{int(6*s)}px {int(8*s)}px;border-radius:6px;}}"
            "QListWidget::item:hover{background:#313244;}"
            "QListWidget::item:selected{background:#45475a;color:#89b4fa;}")
        self.session_list.itemClicked.connect(self._on_session_click)
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._on_session_right_click)
        ll.addWidget(self.session_list)

        new_btn = QPushButton("＋ 新对话")
        new_btn.setStyleSheet(
            f"QPushButton{{background:#313244;color:#cdd6f4;border-radius:{int(8*s)}px;"
            f"padding:{int(7*s)}px;font-size:{int(10*s)}px;font-weight:bold;}}"
            "QPushButton:hover{background:#45475a;}")
        new_btn.clicked.connect(self._new_session)
        ll.addWidget(new_btn)

        self.engine_label = QLabel()
        self.engine_label.setWordWrap(True)
        self.engine_label.setStyleSheet(f"color:#a6adc8;font-size:{int(12*s)}px;padding:4px;font-weight:bold;")
        self._update_engine_label()
        ll.addWidget(self.engine_label)

        ml.addWidget(left)

        # ── Right: Chat ──
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(int(4*s))

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Microsoft YaHei", int(11*s)))
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setLineWrapMode(QTextEdit.WidgetWidth)
        self.chat_display.setStyleSheet(
            f"QTextEdit{{background:#11111b;border:1px solid #313244;border-radius:10px;"
            f"padding:{int(10*s)}px;color:#cdd6f4;}}")
        rl.addWidget(self.chat_display)

        # ── Input bar ──
        input_bar = QWidget()
        input_bar.setStyleSheet("QWidget{background:#181825;border-radius:10px;}")
        il = QHBoxLayout(input_bar)
        il.setContentsMargins(int(8*s), int(6*s), int(6*s), int(6*s))
        il.setSpacing(int(6*s))

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入消息，Enter 发送...")
        self.input_box.setFont(QFont("Microsoft YaHei", int(11*s)))
        self.input_box.setStyleSheet(
            f"QLineEdit{{background:#11111b;border:1px solid #313244;border-radius:{int(8*s)}px;"
            f"padding:{int(9*s)}px {int(12*s)}px;color:#cdd6f4;font-size:{int(11*s)}px;}}"
            "QLineEdit:focus{border:1px solid #89b4fa;}")
        self.input_box.returnPressed.connect(self._send)
        il.addWidget(self.input_box)

        self.send_btn = QPushButton("🚀 发送")
        self.send_btn.setStyleSheet(
            f"QPushButton{{background:#89b4fa;color:#1e1e2e;border-radius:{int(8*s)}px;"
            f"padding:{int(9*s)}px {int(18*s)}px;font-size:{int(11*s)}px;font-weight:bold;}}"
            "QPushButton:hover{background:#b4befe;}"
            "QPushButton:pressed{background:#74c7ec;}")
        self.send_btn.clicked.connect(self._send)
        self.send_btn.setFixedWidth(int(85*s))
        il.addWidget(self.send_btn)

        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet(
            f"QPushButton{{background:#f38ba8;color:#1e1e2e;border-radius:{int(8*s)}px;"
            f"padding:{int(9*s)}px {int(14*s)}px;font-size:{int(11*s)}px;font-weight:bold;}}"
            "QPushButton:hover{background:#fab387;}")
        self.stop_btn.clicked.connect(self._stop)
        self.stop_btn.setFixedWidth(int(72*s))
        self.stop_btn.hide()
        il.addWidget(self.stop_btn)

        rl.addWidget(input_bar)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(int(3*s))
        self.progress.setStyleSheet(
            "QProgressBar{border:none;background:transparent;}"
            "QProgressBar::chunk{background:#89b4fa;border-radius:2px;}")
        self.progress.hide()
        rl.addWidget(self.progress)

        ml.addWidget(right)

    def _build_menu(self):
        s = self._s
        mb = self.menuBar()
        mb.setStyleSheet(
            f"QMenuBar{{background:#11111b;color:#cdd6f4;border-bottom:1px solid #313244;"
            f"padding:2px 8px;font-size:{int(13*s)}px;}}"
            f"QMenuBar::item{{padding:{int(6*s)}px {int(12*s)}px;border-radius:6px;}}"
            f"QMenuBar::item:selected{{background:#313244;}}"
            f"QMenu{{background:#1a1a2e;color:#cdd6f4;border:1px solid #313244;border-radius:8px;"
            f"padding:4px;}}"
            f"QMenu::item{{padding:{int(7*s)}px {int(26*s)}px;border-radius:6px;font-size:{int(12*s)}px;}}"
            f"QMenu::item:selected{{background:#313244;color:#89b4fa;}}"
            f"QMenu::separator{{height:1px;background:#313244;margin:4px 12px;}}")

        f = mb.addMenu("  文件  ")
        a = QAction("📄 新对话", self)
        a.setShortcut(QKeySequence("Ctrl+N"))
        a.triggered.connect(self._new_session)
        f.addAction(a)
        a = QAction("💾 导出对话", self)
        a.setShortcut(QKeySequence("Ctrl+S"))
        a.triggered.connect(self._export)
        f.addAction(a)
        f.addSeparator()
        a = QAction("🚪 退出", self)
        a.setShortcut(QKeySequence("Ctrl+Q"))
        a.triggered.connect(self._logout)
        f.addAction(a)

        s = mb.addMenu("  设置  ")
        s.addAction("🌐 API 设置...", self._show_api_settings)
        s.addAction("⚙️ 模型参数...", self._show_model_params)
        s.addAction("🔧 工具配置...", self._show_tools_settings)
        s.addAction("📁 工作目录...", self._show_workspace_settings)
        s.addAction("💬 系统提示词...", self._show_prompt_settings)
        s.addSeparator()
        s.addAction("🗑 清除对话数据", self._clear_data)

        h = mb.addMenu("  帮助  ")
        h.addAction("ℹ 关于", self._about)

    def _build_statusbar(self):
        self.sb = QStatusBar()
        sb_fs = int(11 * self._s)
        self.sb.setStyleSheet(
            f"QStatusBar{{background:#11111b;color:#a6adc8;border-top:1px solid #313244;"
            f"font-size:{sb_fs}px;padding:2px 8px;}}")
        self.setStatusBar(self.sb)
        self.sb_label = QLabel("就绪 | 设置 API Key 后开始对话")
        self.sb_label.setStyleSheet("color:#a6adc8;")
        self.sb.addWidget(self.sb_label)
        if self.username:
            user_label = QLabel(f"👤 {self.username}")
            user_label.setStyleSheet("color:#89b4fa;font-weight:bold;")
            self.sb.addPermanentWidget(user_label)



    # ── Individual setting panels ──────────────────────────
    def _show_api_settings(self):
        pv = [("openai","OpenAI","https://api.openai.com/v1"),
              ("openrouter","OpenRouter","https://openrouter.ai/api/v1"),
              ("deepseek","DeepSeek","https://api.deepseek.com/v1"),
              ("dashscope","通义千问","https://dashscope.aliyuncs.com/compatible-mode/v1"),
              ("google","Google Gemini","https://generativelanguage.googleapis.com/v1beta/openai"),
              ("anthropic","Anthropic","https://api.anthropic.com/v1")]
        def build(panel):
            cb = QComboBox()
            for pid, pn, _ in pv: cb.addItem(pn, pid)
            idx = cb.findData(settings.get("provider"))
            if idx >= 0: cb.setCurrentIndex(idx)
            panel.add_field("服务商", cb, "provider")
            api = QLineEdit(); api.setEchoMode(QLineEdit.Password); api.setPlaceholderText("sk-...")
            pid = settings.get("provider")
            api.setText(settings.get(f"{pid}_key","") or settings.get("api_key",""))
            panel.add_field("API Key", api, "api_key")
            url = QLineEdit()
            for pvid,_,u in pv:
                if pvid == pid:
                    sv = settings.get("base_url","")
                    url.setText(sv if sv and sv!="https://api.openai.com/v1" else u)
                    break
            panel.add_field("Base URL", url, "base_url")
            model = QLineEdit(); model.setPlaceholderText("deepseek-chat")
            model.setText(settings.get("model",""))
            panel.add_field("模型", model, "model")
            def on_change():
                pid2 = cb.currentData()
                api2 = QLineEdit()
                api2.setText(settings.get(f"{pid2}_key","") or settings.get("api_key",""))
                api.setText(api2.text())
                for pvid2,_,u2 in pv:
                    if pvid2==pid2: sv2=settings.get("base_url",""); url.setText(sv2 if sv2 and sv2!="https://api.openai.com/v1" else u2)
            cb.currentIndexChanged.connect(lambda: on_change())
        dlg = _SettingPanel(self, "API 设置", "🌐", build)
        if dlg.exec_():
            pid = settings.get("provider")
            settings.set(f"{pid}_key", settings.get("api_key"))
            self._update_engine_label()
            self._append_system("API 设置已更新。")

    def _show_model_params(self):
        def build(panel):
            mi = QSpinBox(); mi.setRange(1,100); mi.setValue(settings.get("max_iterations"))
            panel.add_field("最大轮数", mi, "max_iterations")
            mt = QSpinBox(); mt.setRange(256,128000); mt.setValue(settings.get("max_tokens"))
            panel.add_field("Max Tokens", mt, "max_tokens")
            tp = QDoubleSpinBox(); tp.setRange(0,2.0); tp.setSingleStep(0.1); tp.setValue(settings.get("temperature"))
            panel.add_field("Temperature", tp, "temperature")
        dlg = _SettingPanel(self, "模型参数", "⚙️", build)
        if dlg.exec_():
            self._append_system("模型参数已更新。")

    def _show_tools_settings(self):
        def build(panel):
            cb = QComboBox()
            cb.addItem("全部工具 (推荐)","all"); cb.addItem("仅聊天 (无工具)","none")
            cb.addItem("安全模式 (只读)","safe"); cb.addItem("开发模式 (terminal+file)","development")
            cb.addItem("研究模式 (web+vision)","research")
            idx = cb.findData(settings.get("enabled_toolsets"))
            if idx>=0: cb.setCurrentIndex(idx)
            panel.add_field("工具集", cb, "enabled_toolsets")
        dlg = _SettingPanel(self, "工具配置", "🔧", build)
        if dlg.exec_():
            self._append_system("工具配置已更新。")

    def _show_workspace_settings(self):
        def build(panel):
            w = QLineEdit()
            w.setPlaceholderText("留空=EXE目录，或输入路径...")
            w.setText(settings.get("workspace_dir",""))
            panel.add_field("路径", w, "workspace_dir")
            # Browse button
            fl = panel.layout()
            # Add browse row before buttons
            browse_row = QHBoxLayout()
            browse_row.addStretch()
            browse_btn = QPushButton("📂 浏览")
            browse_btn.setStyleSheet("QPushButton{background:#45475a;color:#cdd6f4;border-radius:6px;padding:6px 14px;font-size:12px;} QPushButton:hover{background:#585b70;}")
            def do_browse():
                from PyQt5.QtWidgets import QFileDialog
                d = QFileDialog.getExistingDirectory(panel, "选择工作目录", w.text() or os.path.expanduser("~"))
                if d: w.setText(d)
            browse_btn.clicked.connect(do_browse)
            browse_row.addWidget(browse_btn)
            fl.insertLayout(fl.count()-1, browse_row)
        dlg = _SettingPanel(self, "工作目录", "📁", build)
        if dlg.exec_():
            self._append_system("工作目录已更新。")

    def _show_prompt_settings(self):
        def build(panel):
            sp = QPlainTextEdit()
            sp.setPlainText(settings.get("system_prompt"))
            sp.setPlaceholderText("自定义 AI 的角色和行为...")
            sp.setMinimumHeight(160)
            sp.setStyleSheet("QPlainTextEdit{background:#11111b;border:1px solid #313244;border-radius:8px;padding:10px;font-size:12px;color:#cdd6f4;}")
            panel.add_field("", sp, "system_prompt")
            panel._fields[-1] = ("system_prompt", sp)  # ensure correct key
        dlg = _SettingPanel(self, "系统提示词", "💬", build)
        if dlg.exec_():
            self._append_system("系统提示词已更新。")




    # ── Main Window (Beautiful) ────────────────────────────────
    def _update_engine_label(self):
        if HERMES_AVAILABLE:
            provider = settings.get("provider", "openai")
            model = settings.get("model", "")
            self.engine_label.setText(f"引擎: RAIN ✓\n服务商: {provider}\n模型: {model or '未设置'}")
        else:
            self.engine_label.setText("引擎: 简化模式\n(RAIN核心未加载)")

    # ── Session ──
    def _init_db(self):
        import sqlite3
        user_dir = SETTINGS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        db_path = user_dir / "chat_history.db"
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.execute("""CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY, title TEXT, model TEXT, created_at TEXT
        )""")
        self._db.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT,
            role TEXT, content TEXT, timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )""")
        self._db.commit()
        self._msgs = []  # current session messages in memory

    def _new_session(self):
        self._save_msgs_to_db()
        import uuid
        sid = uuid.uuid4().hex[:12]
        now = datetime.datetime.now().isoformat()
        self._db.execute("INSERT INTO sessions VALUES (?,?,?,?)", (sid, "新对话", settings.get("model",""), now))
        self._db.commit()
        self.current_sid = sid
        self._msgs = []
        self.chat_display.clear()
        self._append_system("新对话已开始。")
        self._refresh_sessions()

    def _save_msgs_to_db(self):
        sid = getattr(self, 'current_sid', None)
        msgs = getattr(self, '_msgs', [])
        if not sid or not msgs:
            return
        # Clear old, save fresh
        self._db.execute("DELETE FROM messages WHERE session_id=?", (sid,))
        now = datetime.datetime.now().isoformat()
        for role, content in msgs:
            self._db.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)",
                (sid, role, content, now)
            )
        # Update title
        first = self._db.execute(
            "SELECT content FROM messages WHERE session_id=? AND role='user' ORDER BY id LIMIT 1", (sid,)
        ).fetchone()
        if first:
            title = first[0][:30].replace("\n", " ")
            self._db.execute("UPDATE sessions SET title=? WHERE id=?", (title, sid))
        self._db.commit()

    def _refresh_sessions(self):
        self.session_list.clear()
        rows = self._db.execute("SELECT id, title, model, created_at FROM sessions ORDER BY created_at DESC").fetchall()
        for sid, title, model, created in rows:
            count = self._db.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (sid,)).fetchone()[0]
            text = f"{title[:25]}\n{model or ''} · {count}条"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, sid)
            self.session_list.addItem(item)

    def _on_session_click(self, item):
        sid = item.data(Qt.UserRole)
        if sid == getattr(self, 'current_sid', None):
            return
        self._save_msgs_to_db()
        self.current_sid = sid
        self._msgs = []
        self.chat_display.clear()
        msgs = self._db.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id", (sid,)
        ).fetchall()
        for role, content in msgs:
            self._msgs.append((role, content))
            if role == "user":
                self._append_user(content)
            else:
                self._append_ai(self._render_md(content))
        self._refresh_sessions()

    def _on_session_right_click(self, pos):
        item = self.session_list.itemAt(pos)
        if not item:
            return
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        del_action = menu.addAction("删除此对话")
        action = menu.exec_(self.session_list.mapToGlobal(pos))
        if action == del_action:
            sid = item.data(Qt.UserRole)
            self._db.execute("DELETE FROM messages WHERE session_id=?", (sid,))
            self._db.execute("DELETE FROM sessions WHERE id=?", (sid,))
            self._db.commit()
            if sid == getattr(self, 'current_sid', None):
                self._new_session()
            else:
                self._refresh_sessions()

    # ── Send ──
    def _send(self):
        text = self.input_box.text().strip()
        if not text:
            return
        if self.worker and self.worker.isRunning():
            return

        self.input_box.clear()
        # Reset per-round permission state (but keep _approve_all for "本次登录同意")
        perm_checker.locked_down = False
        perm_checker._cycle_approved = False
        perm_checker._denied_count = 0
        perm_checker._denied_paths.clear()
        os.environ.pop("RAIN_DENIED", None)  # clear subprocess deny signal
        self._append_user(text)
        # Save user message to memory + DB
        self._msgs.append(("user", text))
        self._save_msgs_to_db()

        self._response_buffer = ""
        self._assistant_block_started = False

        self.send_btn.hide()
        self.stop_btn.show()
        self.progress.show()
        self.sb_label.setText("AI思考中...")

        self.worker = RAINWorker(text, history=getattr(self, '_session_msgs', []))
        # Wire up permission checker
        perm_checker.request = self.worker.perm_request
        self.worker.response_chunk.connect(self._on_chunk)
        self.worker.thinking.connect(self._on_thinking)
        self.worker.tool_start.connect(self._on_tool_start)
        self.worker.tool_complete.connect(self._on_tool_complete)
        self.worker.tool_progress.connect(self._on_tool_progress)
        self.worker.status_msg.connect(lambda m: self.sb_label.setText(m))
        self.worker.notice.connect(lambda m: self._append_system(f"📢 {m}"))
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.perm_request.connect(self._on_perm_request)
        self.worker.start()

    def _on_perm_request(self, tool_name, paths_desc):
        """Show permission dialog for external file access."""
        msg = QMessageBox(self)
        msg.setWindowTitle("权限确认")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"AI/程序尝试在<b>工作目录外</b>操作文件：\n\n<pre>{paths_desc}</pre>")
        msg.setInformativeText(f"工具: {tool_name}\n「本次登录同意」= 登录期间该路径免确认\n「此次同意」= 本轮后续所有操作免确认")
        btn_all = msg.addButton("本次登录同意", QMessageBox.YesRole)
        btn_this = msg.addButton("此次同意", QMessageBox.AcceptRole)
        btn_deny = msg.addButton("不同意", QMessageBox.RejectRole)
        btn_lock = msg.addButton("全部拒绝⚠", QMessageBox.DestructiveRole)
        msg.setDefaultButton(btn_deny)
        msg.exec_()
        clicked = msg.clickedButton()
        if clicked == btn_all:
            perm_checker.grant(approve_all=True)
            self._append_system("🔓 已授权该路径（本次登录不再询问）")
        elif clicked == btn_this:
            perm_checker.grant(approve_all=False)
            self._append_system("✅ 本轮后续操作已全部放行")
        elif clicked == btn_lock:
            perm_checker.deny_all()
            self._append_system("🚫 已强制停止所有操作")
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.terminate()
                self.worker.wait(1000)
            self._reset_ui()
            self.sb_label.setText("操作已拒绝 - 已停止")
        else:
            perm_checker.deny()
            self._append_system(f"⛔ 已拒绝: {tool_name}，停止本轮操作")
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.terminate()
                self.worker.wait(1000)
            self._reset_ui()
            self.sb_label.setText("操作已拒绝 - 已停止")

    def _stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.terminate()
            self.worker.wait(1000)
        self._reset_ui()
        self.sb_label.setText("已停止")
        self._append_system("⏹ 已停止")

    # ── Callbacks ──
    def _on_chunk(self, text):
        if not self._assistant_block_started:
            self._assistant_block_started = True
            # Save cursor position before streaming bubble (for later replacement)
            c = self.chat_display.textCursor()
            c.movePosition(QTextCursor.End)
            self._stream_start_pos = c.position()
            self.chat_display.append(
                '<table align="left" style="margin:6px 0;table-layout:fixed;width:100%;"><tr><td>'
                '<span style="color:#6c7086; font-size:11px;">RAIN</span></td></tr>'
                '<tr><td style="background:#1a1a2e; border-radius:12px 12px 12px 4px; padding:10px 14px; word-wrap:break-word; white-space:pre-wrap;">'
                '<span style="color:#cdd6f4;">'
            )
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        c = self.chat_display.textCursor()
        c.movePosition(QTextCursor.End)
        c.insertHtml(escaped.replace("\n", "<br>"))
        self._response_buffer += text
        self._scroll()

    def _render_md(self, text):
        """Simple markdown to HTML renderer."""
        import re
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Code blocks
        text = re.sub(r'```(\w*)\n(.*?)```', 
            r'<pre style="background:#11111b;color:#a6e3a1;padding:10px;border-radius:6px;font-size:12px;white-space:pre-wrap;word-wrap:break-word;">\2</pre>', 
            text, flags=re.DOTALL)
        # Inline code
        text = re.sub(r'`([^`]+?)`', 
            r'<code style="background:#313244;color:#fab387;padding:1px 5px;border-radius:3px;font-size:12px;">\1</code>', 
            text)
        # Bold **...**
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Italic *...*
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        # Headers
        text = re.sub(r'^### (.+)$', r'<h4 style="color:#89b4fa;margin:8px 0 4px;">\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h3 style="color:#89b4fa;margin:10px 0 4px;">\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h2 style="color:#89b4fa;margin:12px 0 4px;">\1</h2>', text, flags=re.MULTILINE)
        # Lists
        text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', text, flags=re.DOTALL)
        # Line breaks
        text = text.replace("\n", "<br>")
        return text

    def _replace_stream_bubble(self):
        """Replace the raw-text streaming bubble with rendered markdown."""
        rendered = self._render_md(self._response_buffer)
        c = self.chat_display.textCursor()
        c.setPosition(self._stream_start_pos)
        c.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        c.removeSelectedText()
        c.insertHtml(
            '<table align="left" style="margin:6px 0;max-width:85%;"><tr><td>'
            '<span style="color:#6c7086; font-size:11px;">RAIN</span></td></tr>'
            '<tr><td style="background:#1a1a2e; border-radius:12px 12px 12px 4px; padding:10px 14px; word-wrap:break-word; white-space:pre-wrap;">'
            f'<span style="color:#cdd6f4;">{rendered}</span></td></tr></table>'
            f'<br clear="all">'
        )
        self._scroll()

    def _on_thinking(self, text):
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.chat_display.append(
            f'<div style="color:#6c7086; font-style:italic; font-size:11px; margin:2px 0;">💭 {escaped[:300]}</div>'
        )
        self._scroll()

    def _on_tool_start(self, name, args):
        self.chat_display.append(
            f'<div style="margin:2px 0; padding:4px 8px; background:#313244; border-radius:4px; border-left:3px solid #fab387;">'
            f'<span style="color:#fab387;">🔧 {name}</span> '
            f'<span style="color:#a6adc8; font-size:11px;">{args[:200]}</span></div>'
        )
        self._scroll()

    def _on_tool_complete(self, name, result):
        self.chat_display.append(
            f'<div style="margin:0 0 4px 12px; padding:4px 8px; background:#1a1a2e; border-radius:4px; font-size:11px;">'
            f'<span style="color:#a6adc8;">结果: {result[:500]}</span></div>'
        )
        self._scroll()

    def _on_tool_progress(self, name, status):
        self.sb_label.setText(f"🔧 {name}: {status[:80]}")

    def _on_finished(self, response, meta):
        # Save AI response
        if response and response.strip():
            self._msgs.append(("assistant", response))
            self._save_msgs_to_db()
        # Replace streaming raw text with rendered markdown
        if response and response.strip() and hasattr(self, '_stream_start_pos'):
            self._replace_stream_bubble()
        self._reset_ui()
        self.sb_label.setText("就绪")
        self._update_engine_label()
        self._refresh_sessions()

    def _on_error(self, msg):
        self.chat_display.append(
            f'<div style="color:#f38ba8; padding:4px 8px; background:#2e1e1e; border-radius:4px;">'
            f'❌ {msg[:1000]}</div>'
        )
        self._reset_ui()
        self.sb_label.setText("错误")

    def _reset_ui(self):
        self.send_btn.show()
        self.stop_btn.hide()
        self.progress.hide()
        self._assistant_block_started = False
        self.worker = None

    # ── Display helpers ──
    def _append_system(self, text):
        self.chat_display.append(f'<div style="color:#a6adc8; font-style:italic; margin:4px 0;">{text}</div>')

    def _append_user(self, text):
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        name = self.username or "用户"
        self.chat_display.append(
            f'<table align="right" style="margin:6px 0;max-width:85%;"><tr><td align="right">'
            f'<span style="color:#6c7086; font-size:11px;">{name}</span></td></tr>'
            f'<tr><td style="background:#313244; border-radius:12px 12px 4px 12px; padding:10px 14px; word-wrap:break-word; white-space:pre-wrap;">'
            f'<span style="color:#cdd6f4;">{escaped}</span></td></tr></table>'
            f'<br clear="all">'
        )

    def _append_ai(self, html_content):
        self.chat_display.append(
            f'<table align="left" style="margin:6px 0;max-width:85%;"><tr><td>'
            f'<span style="color:#6c7086; font-size:11px;">RAIN</span></td></tr>'
            f'<tr><td style="background:#1a1a2e; border-radius:12px 12px 12px 4px; padding:10px 14px; word-wrap:break-word; white-space:pre-wrap;">'
            f'<span style="color:#cdd6f4;">{html_content}</span></td></tr></table>'
            f'<br clear="all">'
        )

    def _scroll(self):
        if settings.get("auto_scroll"):
            c = self.chat_display.textCursor()
            c.movePosition(QTextCursor.End)
            self.chat_display.setTextCursor(c)

    # ── Actions ──


    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出对话", "chat.html", "HTML (*.html)")
        if path:
            Path(path).write_text(
                f"<html><head><meta charset='utf-8'></head><body>{self.chat_display.toHtml()}</body></html>",
                encoding="utf-8"
            )

    def _clear_data(self):
        r = QMessageBox.question(self, "确认", "确定要清除所有对话数据吗？此操作不可恢复。",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            self._save_msgs_to_db()
            # 清空数据库
            self._db.execute("DELETE FROM messages")
            self._db.execute("DELETE FROM sessions")
            self._db.commit()
            self._msgs = []
            self.current_sid = None
            self.chat_display.clear()
            self.session_list.clear()
            self._new_session()
            self._append_system("🗑️ 所有对话数据已清除")

    def _about(self):
        engine = "RAIN Agent 完整引擎 ✓" if HERMES_AVAILABLE else f"简化引擎 ({_hermes_import_error[:50]}...)"
        QMessageBox.about(self, f"关于 {APP_NAME}",
            f"<b>{APP_NAME} v{APP_VERSION}</b><br><br>"
            f"基于RAIN Agent的完整 Windows 桌面版。<br>"
            f"引擎状态: {engine}<br><br>"
            f"功能: AI对话 · 工具调用 · 代码执行 · 文件操作 · 网页浏览<br>"
            f"技能系统 · 多服务商支持 · 流式响应 · 思考过程"
        )

    def _logout(self):
        self._save_msgs_to_db()
        # 清除记住的登录
        remember_file = SETTINGS_DIR / "remember.json"
        try:
            remember_file.unlink(missing_ok=True)
        except Exception:
            pass
        settings.save()
        QApplication.quit()

    def _heartbeat(self):
        self._heartbeat_count += 1

    def closeEvent(self, e):
        import traceback as _tb
        # Only allow close if user clicked X (spontaneous event)
        if not e.spontaneous():
            e.ignore()
            return
        fs_guard.stop_watching()
        self._save_msgs_to_db()
        settings.set("window_x", self.x())
        settings.set("window_y", self.y())
        settings.set("window_w", self.width())
        settings.set("window_h", self.height())
        super().closeEvent(e)


# ── Main ────────────────────────────────────────────────────
def main():
    # ── Single-instance lock ──
    import ctypes
    _k32 = ctypes.windll.kernel32
    _lock_name = "Global\\RAIN_Desktop_SingleInstance"
    try:
        _lock_handle = _k32.CreateMutexW(None, False, _lock_name)
        if _k32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            sys.exit(0)
    except Exception:
        pass

    # ── Log who launched us ──
    try:
        import psutil
        ppid = os.getppid()
        parent = psutil.Process(ppid)
        parent_name = parent.name()
        # Kill watchdog: if parent is also RAIN.exe, terminate it
        if "RAIN" in parent_name.upper() and ppid != os.getpid():
            try:
                parent.terminate()
                parent.wait(timeout=5)
            except Exception:
                try:
                    parent.kill()
                except Exception:
                    pass
    except Exception as e:
        pass
    # ── Global crash detection ──
    import atexit, signal as _signal
    def _on_exit():
        pass
    atexit.register(_on_exit)
    
    def _global_excepthook(exc_type, exc_value, exc_tb):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    sys.excepthook = _global_excepthook
    
    # Windows structured exception handler for C-level crashes
    try:
        import ctypes
        _kernel32 = ctypes.windll.kernel32
        _old_filter = _kernel32.SetUnhandledExceptionFilter.restype = ctypes.c_void_p
        def _win_exc_handler(exc_info):
            return 0  # EXCEPTION_CONTINUE_SEARCH
        _win_handler = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p)(_win_exc_handler)
        _kernel32.SetUnhandledExceptionFilter(_win_handler)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)

    # Check for remembered login
    remember_file = SETTINGS_DIR / "remember.json"
    auto_login = False
    username = ""

    if remember_file.exists():
        try:
            data = json.loads(remember_file.read_text(encoding="utf-8"))
            remembered_user = data.get("user", "")
            remembered_pass = data.get("pass_hash", "")
            if remembered_user and remembered_pass:
                import sqlite3
                dbp = SETTINGS_DIR / "users.db"
                if dbp.exists():
                    db = sqlite3.connect(str(dbp))
                    row = db.execute("SELECT password FROM users WHERE username=?",
                                   (remembered_user,)).fetchone()
                    db.close()
                    if row and row[0] == remembered_pass:
                        auto_login = True
                        username = remembered_user
                    else:
                        pass
                else:
                    pass
        except Exception as e:
            pass
    if not auto_login:
        dlg = LoginDialog()
        if dlg.exec_() != QDialog.Accepted:
            sys.exit(0)
        username = dlg.username

    # Switch settings to this user (isolation per account)
    settings.switch_user(username)
    perm_checker.reset()   # clear external-path approvals from previous user

    try:
        win = MainWindow(username)
    except Exception as e:
        raise
    win.show()

    if not HERMES_AVAILABLE:
        win._append_system(f"⚠️ RAIN引擎未加载: {_hermes_import_error}")
        win._append_system("将使用OpenAI SDK简易模式。请确保已安装依赖: pip install -r requirements_full.txt")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
