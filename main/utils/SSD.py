import os
import subprocess
import sys

def ensure_pip():
    try:
        import pip
    except ImportError:
        print("Installing pip...")
        subprocess.run([sys.executable, "-m", "ensurepip"])
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

def install_requirements():
    required = ["PyQt5", "pyinstaller", "winshell", "pywin32"]
    for pkg in required:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg])

if __name__ == "__main__":
    print("✅ Checking pip...")
    ensure_pip()
    print("📦 Installing required libraries...")
    install_requirements()
    print("✅ All dependencies installed.")
