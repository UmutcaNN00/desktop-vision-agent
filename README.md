# Desktop Vision Agent

Autonomous visual observation and OS control engine designed for AI agents and automation scripts on Windows.

## Why this exists

Standard coding agents operate purely in terminal shells and cannot view GUI windows, interactive installers, or desktop applications. `desktop-vision-agent` bridges this gap by attaching to the active Windows desktop session, providing screenshot capture, window targeting, and mouse/keyboard automation.

## Features

- **Windows Session Attachment:** Connects background processes to the active user desktop via Win32 APIs.
- **Window Targeting:** Discover, filter, and bring application windows to the foreground.
- **Visual Capture:** Full screen or cropped window capture ready for multimodal LLM analysis.
- **Relative Coordinates:** Click target windows using relative coordinates (e.g. `0.5, 0.5` for center) regardless of resolution or display scaling.
- **Input Controls:** Keyboard input, shortcuts, and mouse scrolling.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start (CLI)

```bash
# List all active visible windows
python -m desktop_vision list-windows

# Capture a full screenshot
python -m desktop_vision capture -o full_desktop.png

# Target and capture a specific window
python -m desktop_vision capture-window "Brave" -o browser.png

# Click inside the center of a window
python -m desktop_vision click-window "Brave" --rx 0.5 --ry 0.5

# Scroll down
python -m desktop_vision scroll -800
```

## Python API

```python
from desktop_vision import DesktopAgent

agent = DesktopAgent()

# Find target window
win = agent.find_window("Brave")
if win:
    agent.focus(win)
    img, info = agent.capture_window(win, output_path="frame.png")
    agent.scroll_down(500)
```

## Repository Structure

```
desktop-vision-agent/
├── desktop_vision/
│   ├── desktop.py       # Desktop session & DPI handling
│   ├── window.py        # Window enumeration & focusing
│   ├── capture.py       # Screen and window capturing
│   ├── input.py         # Mouse and keyboard control
│   ├── agent.py         # Unified DesktopAgent class
│   └── cli.py           # Command line interface
├── examples/
│   ├── installer_automator_demo.py
│   └── feed_reader_demo.py
├── SKILL.md             # Antigravity skill specification
├── requirements.txt
└── README.md
```
