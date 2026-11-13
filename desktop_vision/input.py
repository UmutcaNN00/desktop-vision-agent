"""
Input Controller Module
Provides mouse and keyboard automation capabilities for desktop agents,
including Unicode clipboard typing, mouse hover, and drag-and-drop actions.
"""

import time
from typing import Optional, Tuple, Union
import pyautogui
import pyperclip

from .desktop import attach_desktop
from .window import WindowInfo, bring_to_front, find_window

# Disable failsafe to prevent unexpected mouse corner exceptions during autonomous agent runs
pyautogui.FAILSAFE = False


def is_ascii(text: str) -> bool:
    """Checks if text contains only standard ASCII characters."""
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def move_to(x: int, y: int, duration: float = 0.1):
    """Moves the mouse cursor to the given coordinates."""
    attach_desktop()
    pyautogui.moveTo(x, y, duration=duration)


def hover(x: int, y: int, duration: float = 0.2):
    """Moves the mouse to hover over coordinates (useful for tooltips & menus)."""
    move_to(x, y, duration=duration)


def hover_window(
    window: Union[str, WindowInfo, int],
    rel_x: float = 0.5,
    rel_y: float = 0.5,
    duration: float = 0.2,
    focus: bool = True,
) -> Tuple[int, int]:
    """Hovers over a relative coordinate within a target window."""
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
        time.sleep(0.1)

    target_x = int(win_info.left + win_info.width * rel_x)
    target_y = int(win_info.top + win_info.height * rel_y)
    hover(target_x, target_y, duration=duration)
    return target_x, target_y


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
        time.sleep(0.15)

    target_x = int(win_info.left + win_info.width * rel_x)
    target_y = int(win_info.top + win_info.height * rel_y)

    click(target_x, target_y, button=button)
    return target_x, target_y


def drag_to(x: int, y: int, duration: float = 0.5, button: str = "left"):
    """Drags mouse from current position to target (x, y)."""
    attach_desktop()
    pyautogui.dragTo(x, y, duration=duration, button=button)


def drag_and_drop(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.5,
    button: str = "left"
):
    """Drags an object from (start_x, start_y) and drops at (end_x, end_y)."""
    move_to(start_x, start_y, duration=0.15)
    time.sleep(0.05)
    drag_to(end_x, end_y, duration=duration, button=button)


def scroll(amount: int, x: Optional[int] = None, y: Optional[int] = None):
    """
    Scrolls the mouse wheel.
    Positive value scrolls UP, negative value scrolls DOWN.
    """
    attach_desktop()
    if x is not None and y is not None:
        move_to(x, y)
    pyautogui.scroll(amount)


def paste_text(text: str, restore_clipboard: bool = False, delay: float = 0.05):
    """
    Pastes text using the system clipboard and Ctrl+V.
    Guarantees 100% accurate typing of Turkish characters, emojis, and multiline text.
    """
    attach_desktop()
    prior = None
    if restore_clipboard:
        try:
            prior = pyperclip.paste()
        except Exception:
            pass

    pyperclip.copy(text)
    time.sleep(delay)
    hotkey("ctrl", "v")
    time.sleep(delay)

    if restore_clipboard and prior is not None:
        try:
            pyperclip.copy(prior)
        except Exception:
            pass


def type_text(text: str, interval: float = 0.02, use_clipboard_fallback: bool = True):
    """
    Types text via keyboard. Automatically falls back to clipboard paste
    if non-ASCII (e.g. Turkish characters: ğ, ş, ı, ö, ç, İ or emojis) are detected.
    """
    attach_desktop()
    if use_clipboard_fallback and not is_ascii(text):
        paste_text(text)
    else:
        pyautogui.write(text, interval=interval)


def press_key(key: str):
    """Presses a single key (e.g. 'enter', 'tab', 'esc', 'pagedown')."""
    attach_desktop()
    pyautogui.press(key)


def hotkey(*keys: str):
    """Triggers a keyboard shortcut (e.g. hotkey('ctrl', 'a'))."""
    attach_desktop()
    pyautogui.hotkey(*keys)
