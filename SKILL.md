---
name: desktop-vision
description: >
  Allows autonomous AI agents to inspect, observe, and interact with the active
  Windows desktop. Provides window discovery, multi-monitor screenshot capture,
  anti-lockout window focus, UI Automation (UIA) element inspection, local offline OCR,
  process lifecycle management, smart condition waiting, UAC detection, action tracing,
  and mouse/keyboard automation for GUI workflows and installer navigation.
---

# Desktop Vision & OS Automation Skill (v0.3.0)

This skill grants AI agents the ability to visually observe, semantically inspect, and programmatically interact with the host Windows desktop session with full CUA (Computer-Using Agent) capabilities.

## Core Capabilities

1. **Window Management & Anti-Lockout:** Enumerate open application windows, find by regex title, and reliably restore/focus windows even against Windows foreground lock timeouts (`AttachThreadInput` & Z-order boost).
2. **Window Geometry & Lifecycle:** Move, resize, center, maximize, minimize, and close windows (`WM_CLOSE` or force kill). Launch applications and wait for their windows (`launch_app`).
3. **Multi-Monitor Visual Observation:** High-resolution screenshots of the primary display, specific monitors by index, cropped application windows, or the complete virtual desktop spanning all connected monitors.
4. **Deterministic UI Automation (UIA):** Inspect native UI element hierarchies (buttons, edit fields, checkboxes, tabs, text labels) with bounding boxes and automation IDs. Perform direct programmatic invocations (`InvokePattern`, `TogglePattern`, `ValuePattern`) without moving the mouse.
5. **Local Offline OCR:** Fast, zero-token text recognition powered by the native Windows Media OCR runtime (`winocr`). Automatically searches for on-screen text and clicks text centers (`click_text`).
6. **Unicode & Turkish Keyboard Input:** Safe typing with automatic clipboard fallback (`Ctrl+V` via `pyperclip`) for seamless Turkish characters (`ğ, ş, ı, ö, ç, İ`), multiline strings, and emojis.
7. **Advanced Mouse Control:** Hover over elements/tooltips (`hover`, `hover_window`), drag-and-drop (`drag`, `drag_to`), relative window clicks (`rel_x`, `rel_y`), and wheel scrolling.
8. **Smart Condition Waiting & Change Detection:** Eliminate flaky sleeps with `wait_for_window`, `wait_for_text`, `wait_for_element`, `wait_for_change`, and `wait_until_idle` (settled animations/spinners).
9. **UAC & Secure Desktop Awareness:** Detects when Windows enters User Account Control (`consent.exe`) or secure desktop (`Winlogon`), preventing agent freezes.
10. **Visual Action Tracing & Audit Trail:** Step-by-step recording with annotated screenshots showing red target bullseyes on action coordinates and a structured `actions.jsonl` log.

---

## Quick CLI Usage

Agents can invoke the Python CLI directly via terminal:

### Window & Display Management
- List windows: `python -m desktop_vision list-windows`
- List displays/monitors: `python -m desktop_vision list-monitors`
- Focus window (anti-lockout): `python -m desktop_vision focus "WhatsApp"`
- Resize window: `python -m desktop_vision resize-window "Notepad" 1280 720`
- Center window: `python -m desktop_vision center-window "Notepad" --monitor 0`
- Maximize / Minimize: `python -m desktop_vision maximize-window "Notepad"`
- Close window: `python -m desktop_vision close-window "Notepad" [--force]`

### Visual Capture & Tracing
- Capture primary display: `python -m desktop_vision capture -o screen.png`
- Capture ALL monitors: `python -m desktop_vision capture --all -o all_monitors.png`
- Capture specific monitor: `python -m desktop_vision capture --monitor 1 -o monitor2.png`
- Focus & capture window: `python -m desktop_vision capture-window "Brave" -o brave.png`
- Run with action tracing: `python -m desktop_vision --trace .debug click 500 300`

### Mouse & Keyboard Actions
- Hover: `python -m desktop_vision hover 400 200`
- Hover inside window: `python -m desktop_vision hover-window "Brave" --rx 0.8 --ry 0.2`
- Drag & Drop: `python -m desktop_vision drag 200 300 600 300`
- Click relative position: `python -m desktop_vision click-window "Brave" --rx 0.5 --ry 0.5`
- Type Unicode / Turkish: `python -m desktop_vision type "Giriş Başarılı: Şirin çilekler 🍓"`
- Paste text: `python -m desktop_vision paste "Özel metin yapıştır"`

### UI Automation & OCR
- Inspect window UI tree: `python -m desktop_vision inspect-elements "Brave" --depth 4`
- Click/Invoke UI element: `python -m desktop_vision click-element "Setup" --name "Next" --type Button`
- Extract text via OCR: `python -m desktop_vision ocr --window "Brave"`
- Find & click text: `python -m desktop_vision click-text "Giriş Yap" --window "Brave"`

### Lifecycle & Synchronization
- Launch app & wait: `python -m desktop_vision launch "notepad.exe" --wait-window "Notepad"`
- Wait for window: `python -m desktop_vision wait-window "Setup" --timeout 15`
- Wait for text via OCR: `python -m desktop_vision wait-text "Tamamlandı" --timeout 20`
- Wait for animations to settle: `python -m desktop_vision wait-idle --window "Brave"`
- Check UAC status: `python -m desktop_vision check-uac`

---

## Python Library Usage

```python
from desktop_vision import DesktopAgent

# Enable visual action tracing to .debug folder
agent = DesktopAgent(enable_tracing=True, debug_dir=".debug")

# 1. Check security state
if agent.is_uac_prompt_active:
    print("[WARNING] UAC Prompt is waiting for user consent!")

# 2. Launch application and wait for window
proc, win = agent.launch_app("notepad.exe", wait_window_query="Notepad", timeout=5.0)

if win:
    # 3. Geometry control: resize and center
    agent.resize_window(win, 1280, 720)
    agent.center_window(win, monitor_index=0)
    agent.focus(win)
    
    # 4. Unicode / Turkish writing via clipboard fallback
    agent.type("Başlık: Türkçe karakterler (ç, ğ, ı, ö, ş, ü, İ) ve emojiler 🚀\n")
    
    # 5. Smart waiting: wait for visual state to settle
    agent.wait_until_idle(window=win, settle_time=0.5)

    # 6. Close window gracefully
    agent.close_window(win)
```
