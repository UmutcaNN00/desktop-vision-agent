# Desktop Vision & OS Automation Engine (v0.3.0)

Autonomous Desktop Perception, Multi-Monitor Capture, UI Automation, Native OCR, Process Lifecycle & OS Control Engine for AI Agents.

## Capabilities & Architecture
- **Multi-Monitor:** Seamless virtual desktop geometry across all connected physical displays.
- **Robust Window Focus:** Anti-lockout foreground activation via `AttachThreadInput` and Z-order management.
- **Window Geometry:** Move, resize, center, maximize, minimize, and close windows.
- **UI Automation (UIA):** Deterministic element tree inspection and programmatic invocation without mouse moves.
- **Local Offline OCR:** Zero-token text recognition and text-based clicking via Windows Media OCR (`winocr`).
- **Unicode & Turkish Typing:** Safe keystroke typing with automatic clipboard fallback (`Ctrl+V` via `pyperclip`).
- **Mouse Dynamics:** Precision clicking, window-relative clicks, hover, and drag-and-drop.
- **Smart Synchronization:** Condition-based waiting (`wait_for_window`, `wait_for_text`, `wait_for_element`, `wait_until_idle`).
- **UAC Detection:** Real-time awareness of Windows User Account Control (`consent.exe`) and secure desktop states.
- **Visual Action Tracing:** Audit trail with annotated target bullseyes on action coordinates and `actions.jsonl` step logs.

## CLI Usage
```bash
# Check UAC status
python -m desktop_vision check-uac

# Launch app and wait for window
python -m desktop_vision launch "notepad.exe" --wait-window "Notepad"

# Move & resize window
python -m desktop_vision resize-window "Notepad" 1280 720
python -m desktop_vision center-window "Notepad"

# Type Turkish unicode text
python -m desktop_vision type "Başlık: Türkçe test metni (ç, ğ, ı, ö, ş, ü, İ) 🚀"

# Wait for idle visual state
python -m desktop_vision wait-idle --window "Notepad"

# Close window
python -m desktop_vision close-window "Notepad"
```
