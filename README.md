# Maze 3D

A mobile-first 3D-style maze chase game built with Python and Pygame.

## Run on Windows

1. Install Python 3.10 or newer from https://www.python.org/downloads/windows/.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Controls: W/S or Up/Down to move, A/D or Left/Right to turn. Touch controls are shown on screen on supported touch devices. Escape returns to the menu.

## Android APK

The GitHub Actions workflow builds a debug APK with Buildozer. Open Actions and download the `maze3d-android-apk` artifact after a successful run.

## Project checks

Run `python -m compileall -q .` to check Python syntax.
