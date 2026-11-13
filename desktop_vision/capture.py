"""
Screen Capture Module
Captures full displays, individual application windows, or specific screen regions.
"""

import os
import time
from typing import Optional, Tuple, Union
from PIL import Image, ImageGrab

from .desktop import attach_desktop, set_dpi_awareness
from .window import WindowInfo, bring_to_front, find_window


def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
    """
    Captures a full screenshot or a specified bounding box (left, top, right, bottom).
    """
    attach_desktop()
    set_dpi_awareness()
    return ImageGrab.grab(bbox=region)


def capture_window(
    window: Union[str, WindowInfo, int],
    focus: bool = True,
    delay: float = 0.3
) -> Tuple[Image.Image, WindowInfo]:
    """
    Captures the specified application window.
    Brings the window to focus, calculates its bounds, and crops the capture.
    """
    win_info: Optional[WindowInfo] = None
    if isinstance(window, WindowInfo):
        win_info = window
    elif isinstance(window, str):
        win_info = find_window(window)
        if not win_info:
            raise ValueError(f"Window with title matching '{window}' not found.")
    elif isinstance(window, int):
        from .window import get_window_rect
        rect = get_window_rect(window)
        win_info = WindowInfo(hwnd=window, title="Window", rect=rect)
    else:
        raise TypeError("window must be a title string, WindowInfo, or hwnd integer.")

    if focus:
        bring_to_front(win_info.hwnd)
        if delay > 0:
            time.sleep(delay)

    # Re-fetch bounds in case focusing shifted position
    from .window import get_window_rect
    updated_rect = get_window_rect(win_info.hwnd)
    win_info.rect = updated_rect

    img = capture_screen(region=updated_rect)
    return img, win_info


def save_capture(
    image: Image.Image,
    output_path: str,
    create_dirs: bool = True
) -> str:
    """Saves the captured image to disk."""
    if create_dirs:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    image.save(output_path)
    return os.path.abspath(output_path)
