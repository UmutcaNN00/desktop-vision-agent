"""
Desktop Vision & OS Automation Package
"""

from .desktop import attach_desktop, get_screen_size, set_dpi_awareness
from .window import WindowInfo, bring_to_front, find_window, find_windows, list_windows
from .capture import capture_screen, capture_window, save_capture
from .input import (
    click,
    click_window,
    double_click,
    hotkey,
    move_to,
    press_key,
    right_click,
    scroll,
    type_text,
)
from .agent import DesktopAgent

__version__ = "0.1.0"
__all__ = [
    "DesktopAgent",
    "attach_desktop",
    "get_screen_size",
    "set_dpi_awareness",
    "WindowInfo",
    "list_windows",
    "find_window",
    "find_windows",
    "bring_to_front",
    "capture_screen",
    "capture_window",
    "save_capture",
    "move_to",
    "click",
    "double_click",
    "right_click",
    "click_window",
    "scroll",
    "type_text",
    "press_key",
    "hotkey",
]
