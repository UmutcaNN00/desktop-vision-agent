"""
Input Controller Module
Provides mouse and keyboard automation capabilities for desktop agents.
"""

import time
from typing import Optional, Union, Tuple
import pyautogui

from .desktop import attach_desktop
from .window import WindowInfo, bring_to_front, find_window

# Disable failsafe to prevent unexpected mouse corner exceptions during autonomous agent runs
pyautogui.FAILSAFE = False


def move_to(x: int, y: int, duration: float = 0.1):
    """Moves the mouse cursor to the given coordinates."""
    attach_desktop()
    pyautogui.moveTo(x, y, duration=duration)


def click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1):
    """Clicks at the current or specified coordinates."""
    attach_desktop()
    if x is not None and y is not None:
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
    else:
        pyautogui.click(button=button, clicks=clicks)


def double_click(x: Optional[int] = None, y: Optional[int] = None):
    """Performs a double-click."""
    click(x=x, y=y, clicks=2)


def right_click(x: Optional[int] = None, y: Optional[int] = None):
    """Performs a right-click."""
    click(x=x, y=y, button="right")


def click_window(
    window: Union[str, WindowInfo, int],
    rel_x: float = 0.5,
    rel_y: float = 0.5,
    focus: bool = True,
    button: str = "left"
) -> Tuple[int, int]:
    """
    Clicks at a relative position within a target window.
    rel_x=0.5, rel_y=0.5 clicks the exact center of the window.
    rel_x=0.0, rel_y=0.0 is top-left, 1.0, 1.0 is bottom-right.
    """
    win_info: Optional[WindowInfo] = None
    if isinstance(window, WindowInfo):
        win_info = window
    elif isinstance(window, str):
        win_info = find_window(window)
        if not win_info:
            raise ValueError(f"Window matching '{window}' not found.")
    elif isinstance(window, int):
        from .window import get_window_rect
        rect = get_window_rect(window)
        win_info = WindowInfo(hwnd=window, title="Window", rect=rect)

    if focus:
        bring_to_front(win_info.hwnd)
        time.sleep(0.2)

    # Calculate target pixel
    target_x = int(win_info.left + win_info.width * rel_x)
    target_y = int(win_info.top + win_info.height * rel_y)

    click(target_x, target_y, button=button)
    return target_x, target_y


def scroll(amount: int, x: Optional[int] = None, y: Optional[int] = None):
    """
    Scrolls the mouse wheel.
    Positive value scrolls UP, negative value scrolls DOWN.
    """
    attach_desktop()
    if x is not None and y is not None:
        move_to(x, y)
    pyautogui.scroll(amount)


def type_text(text: str, interval: float = 0.02):
    """Types out text with optional per-keystroke interval."""
    attach_desktop()
    pyautogui.write(text, interval=interval)


def press_key(key: str):
    """Presses a single key (e.g. 'enter', 'tab', 'esc', 'pagedown')."""
    attach_desktop()
    pyautogui.press(key)


def hotkey(*keys: str):
    """Triggers a keyboard shortcut (e.g. hotkey('ctrl', 'a'))."""
    attach_desktop()
    pyautogui.hotkey(*keys)
