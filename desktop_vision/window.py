"""
Window Management Module
Finds, enumerates, inspects, and focuses application windows on Windows OS.
"""

import ctypes
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .desktop import attach_desktop


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)

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

    @property
    def center(self) -> Tuple[int, int]:
        return (self.left + self.width // 2, self.top + self.height // 2)


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Retrieves the bounding box of a window."""
    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]
    rect = RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


def list_windows(visible_only: bool = True) -> List[WindowInfo]:
    """Lists all active windows with titles."""
    u32 = ctypes.windll.user32
    hdesk = attach_desktop()
    windows: List[WindowInfo] = []

    def enum_cb(hwnd, _):
        if not visible_only or u32.IsWindowVisible(hwnd):
            length = u32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                u32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.strip()
                if title:
                    r = get_window_rect(hwnd)
                    windows.append(WindowInfo(hwnd=hwnd, title=title, rect=r))
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    u32.EnumDesktopWindows(hdesk, WNDENUMPROC(enum_cb), 0)
    return windows


def find_windows(title_query: str, exact: bool = False, case_sensitive: bool = False) -> List[WindowInfo]:
    """Finds windows matching the title query."""
    all_wins = list_windows(visible_only=True)
    matches = []
    
    pattern = title_query if exact else re.escape(title_query)
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(f"^{pattern}$" if exact else pattern, flags)

    for win in all_wins:
        if regex.search(win.title):
            matches.append(win)
    return matches


def find_window(title_query: str) -> Optional[WindowInfo]:
    """Finds the first window matching the query."""
    wins = find_windows(title_query)
    return wins[0] if wins else None


def bring_to_front(hwnd: int) -> bool:
    """Restores and focuses a window to the front."""
    u32 = ctypes.windll.user32
    attach_desktop()
    # 9 = SW_RESTORE
    u32.ShowWindow(hwnd, 9)
    u32.BringWindowToTop(hwnd)
    return bool(u32.SetForegroundWindow(hwnd))
