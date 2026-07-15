"""RAIN Launcher — tiny EXE that spawns the portable Python + RAIN_desktop.py."""
import os
import sys
import subprocess

def main():
    base = os.path.dirname(sys.executable)
    python_dir = os.path.join(base, "python")
    python = os.path.join(python_dir, "pythonw.exe")
    script = os.path.join(base, "RAIN_desktop.py")

    if not os.path.isfile(python):
        python = os.path.join(python_dir, "python.exe")

    env = os.environ.copy()
    env["PYTHONHOME"] = python_dir
    env["PYTHONPATH"] = os.path.join(python_dir, "Lib", "site-packages")

    # CREATE_NO_WINDOW to avoid console flash
    subprocess.Popen(
        [python, script],
        env=env,
        creationflags=0x08000000 if sys.platform == "win32" else 0,
        cwd=base,
    )

if __name__ == "__main__":
    main()
