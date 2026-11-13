"""
Screen Capture Module
Captures full displays, individual application windows, or specific screen regions.
"""

import os
import time
from typing import Optional, Tuple, Union
from PIL import Image, ImageGrab

from .desktop import attach_desktop, get_monitors, get_screen_size, get_virtual_screen_bounds, set_dpi_awareness
from .window import WindowInfo, bring_to_front, find_window


def capture_screen(
    region: Optional[Tuple[int, int, int, int]] = None,
    all_monitors: bool = False,
    monitor_index: Optional[int] = None,
) -> Image.Image:
    """
    Captures a full screenshot, a specific monitor, or a specified bounding box.
    Gracefully handles multi-monitor coordinates and DPI boundaries.
    """
    attach_desktop()
    set_dpi_awareness()

    if monitor_index is not None:
        monitors = get_monitors()
        if 0 <= monitor_index < len(monitors):
            full = ImageGrab.grab(all_screens=True)
            vx, vy, _, _ = get_virtual_screen_bounds()
            m = monitors[monitor_index]
            crop_box = (m.left - vx, m.top - vy, m.right - vx, m.bottom - vy)
            return full.crop(crop_box)
        raise IndexError(f"Monitor index {monitor_index} out of range (0-{len(monitors) - 1})")

    if all_monitors:
        return ImageGrab.grab(all_screens=True)

    if region is not None:
        sw, sh = get_screen_size()
        left, top, right, bottom = region
        # If strictly within primary screen, fast grab
        if left >= 0 and top >= 0 and right <= sw and bottom <= sh:
            try:
                return ImageGrab.grab(bbox=region)
            except Exception:
                pass
        # Fallback/multi-monitor: grab full virtual desktop and crop
        full = ImageGrab.grab(all_screens=True)
        vx, vy, _, _ = get_virtual_screen_bounds()
        crop_box = (left - vx, top - vy, right - vx, bottom - vy)
        return full.crop(crop_box)

    return ImageGrab.grab()



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
