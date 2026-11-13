"""
DesktopAgent Orchestrator
High-level interface combining visual observation and OS control for autonomous agents.
"""

import time
from typing import List, Optional, Tuple, Union
from PIL import Image

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


class DesktopAgent:
    """
    Unified Desktop Agent interface for visual perception and OS control.
    """

    def __init__(self):
        set_dpi_awareness()
        attach_desktop()

    @property
    def screen_size(self) -> Tuple[int, int]:
        """Returns primary display resolution."""
        return get_screen_size()

    # --- Perception / Vision ---

    def list_windows(self, visible_only: bool = True) -> List[WindowInfo]:
        """Lists active windows with title and coordinates."""
        return list_windows(visible_only=visible_only)

    def find_window(self, query: str) -> Optional[WindowInfo]:
        """Finds first window matching the query."""
        return find_window(query)

    def find_windows(self, query: str) -> List[WindowInfo]:
        """Finds all windows matching the query."""
        return find_windows(query)

    def capture(
        self,
        output_path: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Image.Image:
        """Captures the full screen or region."""
        img = capture_screen(region=region)
        if output_path:
            save_capture(img, output_path)
        return img

    def capture_window(
        self,
        window: Union[str, WindowInfo, int],
        output_path: Optional[str] = None,
        focus: bool = True
    ) -> Tuple[Image.Image, WindowInfo]:
        """Brings target window to focus and captures it."""
        img, win = capture_window(window, focus=focus)
        if output_path:
            save_capture(img, output_path)
        return img, win

    # --- Action / Interaction ---

    def focus(self, window: Union[str, WindowInfo, int]) -> bool:
        """Brings the window to the front."""
        if isinstance(window, str):
            win = find_window(window)
            if not win:
                return False
            return bring_to_front(win.hwnd)
        elif isinstance(window, WindowInfo):
            return bring_to_front(window.hwnd)
        elif isinstance(window, int):
            return bring_to_front(window)
        return False

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left"):
        """Clicks at (x, y)."""
        click(x=x, y=y, button=button)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """Double clicks at (x, y)."""
        double_click(x=x, y=y)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """Right clicks at (x, y)."""
        right_click(x=x, y=y)

    def click_window(
        self,
        window: Union[str, WindowInfo, int],
        rel_x: float = 0.5,
        rel_y: float = 0.5,
        button: str = "left"
    ) -> Tuple[int, int]:
        """Clicks relative to the target window."""
        return click_window(window, rel_x=rel_x, rel_y=rel_y, button=button)

    def scroll_down(self, amount: int = 500, x: Optional[int] = None, y: Optional[int] = None):
        """Scrolls down."""
        scroll(-abs(amount), x=x, y=y)

    def scroll_up(self, amount: int = 500, x: Optional[int] = None, y: Optional[int] = None):
        """Scrolls up."""
        scroll(abs(amount), x=x, y=y)

    def type(self, text: str, interval: float = 0.02):
        """Types text on keyboard."""
        type_text(text, interval=interval)

    def press(self, key: str):
        """Presses a key."""
        press_key(key)

    def hotkey(self, *keys: str):
        """Presses keyboard shortcut combinations."""
        hotkey(*keys)

    def wait(self, seconds: float):
        """Pauses execution."""
        time.sleep(seconds)
