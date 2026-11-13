"""
Smart Waiting & Change Detection Module
Provides condition-based synchronization (wait for window, text, UI element, or screen change)
eliminating flaky fixed time.sleep calls during agent workflows.
"""

import time
from typing import Any, Optional, Tuple, Union
from PIL import ImageChops

from .capture import capture_screen, capture_window
from .elements import find_element
from .ocr import find_text
from .window import WindowInfo, find_window


def wait_for_window(
    title_query: str,
    timeout: float = 10.0,
    interval: float = 0.5,
) -> Optional[WindowInfo]:
    """
    Waits until a window matching the title query appears.
    Returns the WindowInfo when found, or None if timed out.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        win = find_window(title_query)
        if win:
            return win
        time.sleep(interval)
    return None


def wait_for_text(
    query: str,
    window: Optional[Union[str, WindowInfo, int]] = None,
    timeout: float = 10.0,
    interval: float = 0.5,
    exact: bool = False,
    lang: Optional[str] = None,
) -> bool:
    """
    Waits until the specified text appears on screen or in a window via offline OCR.
    Returns True when text is found, False if timed out.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        matches = find_text(query, window=window, exact=exact, lang=lang)
        if matches:
            return True
        time.sleep(interval)
    return False


def wait_for_element(
    window: Union[str, WindowInfo, int],
    name: Optional[str] = None,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None,
    timeout: float = 10.0,
    interval: float = 0.5,
) -> bool:
    """
    Waits until a native UI element matching criteria appears in the window.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        elem = find_element(
            window,
            name=name,
            control_type=control_type,
            automation_id=automation_id,
        )
        if elem:
            return True
        time.sleep(interval)
    return False


def _get_snapshot(region: Optional[Tuple[int, int, int, int]] = None, window: Optional[Any] = None):
    if window is not None:
        img, _ = capture_window(window, focus=False)
        return img
    return capture_screen(region=region)


def wait_for_change(
    region: Optional[Tuple[int, int, int, int]] = None,
    window: Optional[Union[str, WindowInfo, int]] = None,
    timeout: float = 5.0,
    interval: float = 0.2,
) -> bool:
    """
    Waits until visual pixels in the target window or region change.
    Returns True if a visual change occurred within timeout, False otherwise.
    """
    base_img = _get_snapshot(region=region, window=window)
    start_time = time.time()

    while time.time() - start_time < timeout:
        time.sleep(interval)
        current_img = _get_snapshot(region=region, window=window)
        diff = ImageChops.difference(base_img, current_img)
        bbox = diff.getbbox()
        if bbox:
            # Found pixel change
            return True

    return False


def wait_until_idle(
    region: Optional[Tuple[int, int, int, int]] = None,
    window: Optional[Union[str, WindowInfo, int]] = None,
    timeout: float = 10.0,
    settle_time: float = 0.5,
    interval: float = 0.2,
) -> bool:
    """
    Waits until the screen or window stops changing for at least settle_time seconds.
    Crucial for ensuring page loads, spinners, or animations have settled before acting.
    """
    start_time = time.time()
    last_change_time = time.time()
    last_img = _get_snapshot(region=region, window=window)

    while time.time() - start_time < timeout:
        time.sleep(interval)
        current_img = _get_snapshot(region=region, window=window)
        diff = ImageChops.difference(last_img, current_img)
        last_img = current_img

        if diff.getbbox():
            last_change_time = time.time()
        else:
            if time.time() - last_change_time >= settle_time:
                return True

    return False
