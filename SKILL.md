---
name: desktop-vision
description: >
  Allows autonomous AI agents to inspect, observe, and interact with the active
  Windows desktop. Provides window discovery, screenshot capture, focus management,
  and mouse/keyboard automation for GUI workflows and installer navigation.
---

# Desktop Vision & OS Automation Skill

This skill grants AI agents the ability to visually observe and programmatically interact with the host Windows desktop session.

## Core Capabilities

1. **Window Management:** List open application windows, find by title, and bring windows to the foreground.
2. **Visual Observation:** High-resolution screenshots of the whole display or cropped to specific application windows.
3. **Desktop Input:** Safe keyboard typing, key presses, relative window clicks, and mouse scrolling.

## Quick CLI Usage

Agents can invoke the Python CLI directly via terminal:

- List windows: `python -m desktop_vision list-windows`
- Capture full screen: `python -m desktop_vision capture -o screen.png`
- Focus & capture window: `python -m desktop_vision capture-window "Brave" -o brave.png`
- Focus window: `python -m desktop_vision focus "Brave"`
- Click relative position: `python -m desktop_vision click-window "Brave" --rx 0.5 --ry 0.5`
- Scroll: `python -m desktop_vision scroll -500`
- Type text: `python -m desktop_vision type "hello"`
- Press key: `python -m desktop_vision press enter`

## Python Library Usage

```python
from desktop_vision import DesktopAgent

agent = DesktopAgent()

# Find and focus target application
win = agent.find_window("Brave")
if win:
    agent.focus(win)
    # Capture cropped window for multimodal inspection
    img, info = agent.capture_window(win, output_path="view.png")
    
    # Scroll content
    agent.scroll_down(600)
```
