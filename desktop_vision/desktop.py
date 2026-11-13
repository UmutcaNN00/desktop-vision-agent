"""
Desktop Session, DPI & Multi-Monitor Management Module for Windows
Handles Session attachment, DPI awareness, and multi-monitor geometry mapping.
"""

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class MonitorInfo:
    index: int
    device: str
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    is_primary: bool

    @property
    def left(self) -> int:
        return self.rect[0]

    @property
    def top(self) -> int:
        return self.rect[1]

    @property
    def right(self) -> int:
        return self.rect[2]

    @property
    def bottom(self) -> int:
        return self.rect[3]

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)


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


_ATTACHED_DESKTOP: Optional[int] = None


def attach_desktop() -> Optional[int]:
    """
    Attaches the calling thread to the active user desktop.
    Critical for background agent processes or scripts running via CLI/SSH
    to interact with the user's GUI session.
    """
    global _ATTACHED_DESKTOP
    u32 = ctypes.windll.user32
    u32.OpenInputDesktop.restype = wintypes.HANDLE
    u32.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    u32.SetThreadDesktop.restype = wintypes.BOOL
    u32.SetThreadDesktop.argtypes = [wintypes.HANDLE]

    if _ATTACHED_DESKTOP:
        return _ATTACHED_DESKTOP

    # 0x01FF = DESKTOP_ALL_ACCESS
    hdesk = u32.OpenInputDesktop(0, False, 0x01FF)
    if hdesk:
        if u32.SetThreadDesktop(hdesk):
            _ATTACHED_DESKTOP = hdesk
        return hdesk
    return None


# Initialize desktop attachment and DPI awareness as early as possible
attach_desktop()
set_dpi_awareness()




def get_screen_size() -> Tuple[int, int]:
    """
    Returns (width, height) of the primary display.
    """
    u32 = ctypes.windll.user32
    return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)


def get_virtual_screen_bounds() -> Tuple[int, int, int, int]:
    """
    Returns (left, top, width, height) of the full virtual desktop spanning all monitors.
    """
    u32 = ctypes.windll.user32
    # SM_XVIRTUALSCREEN = 76, SM_YVIRTUALSCREEN = 77, SM_CXVIRTUALSCREEN = 78, SM_CYVIRTUALSCREEN = 79
    left = u32.GetSystemMetrics(76)
    top = u32.GetSystemMetrics(77)
    width = u32.GetSystemMetrics(78)
    height = u32.GetSystemMetrics(79)
    return left, top, width, height


def get_monitors() -> List[MonitorInfo]:
    """
    Enumerates all physical monitors and their bounding boxes.
    """
    set_dpi_awareness()
    attach_desktop()

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    class MONITORINFOEXW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", RECT),
            ("rcWork", RECT),
            ("dwFlags", wintypes.DWORD),
            ("szDevice", wintypes.WCHAR * 32),
        ]

    monitors: List[MonitorInfo] = []

    def enum_cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
        info = MONITORINFOEXW()
        info.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(hMonitor, ctypes.byref(info))
        rc = info.rcMonitor
        is_primary = bool(info.dwFlags & 1)
        monitors.append(
            MonitorInfo(
                index=len(monitors),
                device=info.szDevice,
                rect=(rc.left, rc.top, rc.right, rc.bottom),
                is_primary=is_primary,
            )
        )
        return True

    CB = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, CB(enum_cb), 0)
    return monitors


def get_active_desktop_name() -> str:
    """
    Returns the name of the currently active Windows input desktop
    (e.g., 'Default', 'Winlogon', 'Screen-saver').
    """
    u32 = ctypes.windll.user32
    # 0x0001 = DESKTOP_READOBJECTS
    hdesk = u32.OpenInputDesktop(0, False, 0x0001)
    if not hdesk:
        err = ctypes.GetLastError()
        if err == 5:  # ERROR_ACCESS_DENIED
            return "SecureDesktop/UAC"
        return "Unknown"
    try:
        name = ctypes.create_unicode_buffer(256)
        needed = ctypes.c_ulong()
        u32.GetUserObjectInformationW(hdesk, 2, name, ctypes.sizeof(name), ctypes.byref(needed))
        return name.value
    finally:
        u32.CloseDesktop(hdesk)


def is_uac_active() -> bool:
    """
    Checks if Windows User Account Control (UAC) consent dialog (consent.exe) is currently active.
    """
    try:
        import psutil
        for p in psutil.process_iter(["name"]):
            if p.info["name"] and p.info["name"].lower() == "consent.exe":
                return True
    except Exception:
        pass
    return False


def is_secure_desktop_active() -> bool:
    """
    Detects if the session has switched to a secure desktop (UAC prompt,
    lock screen, or Winlogon) which locks user input automation.
    """
    if is_uac_active():
        return True
    desktop_name = get_active_desktop_name()
    return desktop_name.lower() not in ("default", "")


