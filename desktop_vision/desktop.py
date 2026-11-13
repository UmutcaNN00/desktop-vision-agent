"""
Desktop Session & DPI Management Module for Windows
Handles Session attachment and DPI awareness to ensure accurate coordinate mapping.
"""

import ctypes
from typing import Optional, Tuple


def set_dpi_awareness() -> bool:
    """
    Enables Per-Monitor DPI Awareness so screen capture and mouse
    coordinates map 1:1 with actual physical pixels.
    """
    try:
        # Per-Monitor V2 DPI awareness (Windows 10/11)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
        return True
    except Exception:
        try:
            # Fallback to Per-Monitor DPI awareness
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            return True
        except Exception:
            try:
                # Fallback to system DPI aware
                ctypes.windll.user32.SetProcessDPIAware()
                return True
            except Exception:
                return False


def attach_desktop() -> Optional[int]:
    """
    Attaches the calling thread to the active user desktop.
    Critical for background agent processes or scripts running via CLI/SSH
    to interact with the user's GUI session.
    """
    u32 = ctypes.windll.user32
    # 0x01FF = DESKTOP_ALL_ACCESS
    hdesk = u32.OpenInputDesktop(0, False, 0x01FF)
    if hdesk:
        u32.SetThreadDesktop(hdesk)
        return hdesk
    return None


def get_screen_size() -> Tuple[int, int]:
    """
    Returns (width, height) of the primary display.
    """
    u32 = ctypes.windll.user32
    return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
