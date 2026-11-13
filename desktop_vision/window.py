"""
Window Management Module
Finds, enumerates, inspects, and focuses application windows on Windows OS.
"""

import ctypes
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
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
    """
    Restores and focuses a window to the front with anti-lockout handling.
    Bypasses Windows SetForegroundWindow restrictions by attaching thread input
    and temporarily raising z-order.
    """
    u32 = ctypes.windll.user32
    k32 = ctypes.windll.kernel32
    attach_desktop()

    if not u32.IsWindow(hwnd):
        return False

    current_tid = k32.GetCurrentThreadId()
    target_tid = u32.GetWindowThreadProcessId(hwnd, None)
    fg_hwnd = u32.GetForegroundWindow()
    fg_tid = u32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0

    attached_current = False
    attached_fg = False

    try:
        # Attach threads to borrow foreground activation permission
        if target_tid and current_tid != target_tid:
            attached_current = bool(u32.AttachThreadInput(current_tid, target_tid, True))
        if target_tid and fg_tid and fg_tid != target_tid:
            attached_fg = bool(u32.AttachThreadInput(fg_tid, target_tid, True))

        # Restore if minimized (SW_RESTORE = 9), else show normally (SW_SHOW = 5)
        if u32.IsIconic(hwnd):
            u32.ShowWindow(hwnd, 9)
        else:
            u32.ShowWindow(hwnd, 5)

        u32.BringWindowToTop(hwnd)

        # Force window to top of Z-order and immediately release topmost lock
        # HWND_TOPMOST = -1, HWND_NOTOPMOST = -2, SWP_NOMOVE = 0x0002, SWP_NOSIZE = 0x0001
        u32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
        u32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002)

        res = bool(u32.SetForegroundWindow(hwnd))
        u32.SetActiveWindow(hwnd)
        return res
    finally:
        # Clean up attached threads
        if attached_current:
            u32.AttachThreadInput(current_tid, target_tid, False)
        if attached_fg:
            u32.AttachThreadInput(fg_tid, target_tid, False)


def _resolve_hwnd(window: Union[str, WindowInfo, int]) -> Optional[int]:
    """Helper to convert window title, WindowInfo, or hwnd to an integer HWND."""
    if isinstance(window, int):
        return window
    if isinstance(window, WindowInfo):
        return window.hwnd
    if isinstance(window, str):
        win = find_window(window)
        return win.hwnd if win else None
    return None


def resize_window(window: Union[str, WindowInfo, int], width: int, height: int) -> bool:
    """Resizes the target window to specified width and height in pixels."""
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        return False
    u32 = ctypes.windll.user32
    rect = get_window_rect(hwnd)
    # SWP_NOMOVE = 0x0002, SWP_NOZORDER = 0x0004
    return bool(u32.SetWindowPos(hwnd, 0, rect[0], rect[1], width, height, 0x0002 | 0x0004))


def move_window(window: Union[str, WindowInfo, int], x: int, y: int) -> bool:
    """Moves the top-left corner of the target window to (x, y) coordinates."""
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        return False
    u32 = ctypes.windll.user32
    rect = get_window_rect(hwnd)
    w = max(0, rect[2] - rect[0])
    h = max(0, rect[3] - rect[1])
    # SWP_NOSIZE = 0x0001, SWP_NOZORDER = 0x0004
    return bool(u32.SetWindowPos(hwnd, 0, x, y, w, h, 0x0001 | 0x0004))


def center_window(window: Union[str, WindowInfo, int], monitor_index: int = 0) -> bool:
    """Centers the target window on the specified physical monitor."""
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        return False
    from .desktop import get_monitors
    mons = get_monitors()
    if not (0 <= monitor_index < len(mons)):
        monitor_index = 0
    m = mons[monitor_index]
    rect = get_window_rect(hwnd)
    w = max(0, rect[2] - rect[0])
    h = max(0, rect[3] - rect[1])
    target_x = m.left + (m.width - w) // 2
    target_y = m.top + (m.height - h) // 2
    return move_window(hwnd, target_x, target_y)


def maximize_window(window: Union[str, WindowInfo, int]) -> bool:
    """Maximizes the target window (SW_MAXIMIZE)."""
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        return False
    return bool(ctypes.windll.user32.ShowWindow(hwnd, 3))


def minimize_window(window: Union[str, WindowInfo, int]) -> bool:
    """Minimizes the target window (SW_MINIMIZE)."""
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        return False
    return bool(ctypes.windll.user32.ShowWindow(hwnd, 6))


def close_window(window: Union[str, WindowInfo, int], force: bool = False) -> bool:
    """
    Closes the target window gracefully via WM_CLOSE or forcefully terminates its process.
    """
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        return False
    u32 = ctypes.windll.user32
    if force:
        pid = ctypes.wintypes.DWORD()
        u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value:
            # PROCESS_TERMINATE = 0x0001
            hproc = ctypes.windll.kernel32.OpenProcess(0x0001, False, pid.value)
            if hproc:
                res = bool(ctypes.windll.kernel32.TerminateProcess(hproc, 0))
                ctypes.windll.kernel32.CloseHandle(hproc)
                return res
        return False
    else:
        # WM_CLOSE = 0x0010
        return bool(u32.PostMessageW(hwnd, 0x0010, 0, 0))


