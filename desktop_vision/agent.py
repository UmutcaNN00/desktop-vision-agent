"""
DesktopAgent Orchestrator
High-level unified interface combining visual observation, UI automation,
native OCR, lifecycle management, action tracing, and OS control for autonomous agents.
"""

import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image

from .desktop import (
    MonitorInfo,
    attach_desktop,
    get_active_desktop_name,
    get_monitors,
    get_screen_size,
    get_virtual_screen_bounds,
    is_secure_desktop_active,
    is_uac_active,
    set_dpi_awareness,
)
from .window import (
    WindowInfo,
    bring_to_front,
    center_window,
    close_window,
    find_window,
    find_windows,
    list_windows,
    maximize_window,
    minimize_window,
    move_window,
    resize_window,
)
from .capture import capture_screen, capture_window, save_capture
from .elements import (
    UIElement,
    click_element,
    find_element,
    find_elements,
    inspect_elements,
    set_element_text,
)
from .ocr import (
    TextMatch,
    click_text,
    find_text,
    get_available_languages,
    recognize_text,
)
from .input import (
    click,
    click_window,
    double_click,
    drag_and_drop,
    drag_to,
    hotkey,
    hover,
    hover_window,
    move_to,
    paste_text,
    press_key,
    right_click,
    scroll,
    type_text,
)
from .waiting import (
    wait_for_change,
    wait_for_element,
    wait_for_text,
    wait_for_window,
    wait_until_idle,
)
from .lifecycle import (
    is_process_running,
    launch_app,
    terminate_process,
)
from .tracing import ActionRecord, ActionTracer


class DesktopAgent:
    """
    Unified Desktop Agent interface for visual perception, UI automation,
    process lifecycle, and OS control.
    """

    def __init__(self, enable_tracing: bool = False, debug_dir: str = ".debug"):
        set_dpi_awareness()
        attach_desktop()
        self.tracer = ActionTracer(output_dir=debug_dir, enabled=enable_tracing)

    # --- System, Display & Security State ---

    @property
    def screen_size(self) -> Tuple[int, int]:
        """Returns primary display resolution (width, height)."""
        return get_screen_size()

    @property
    def virtual_screen_bounds(self) -> Tuple[int, int, int, int]:
        """Returns virtual desktop bounds across all displays (left, top, width, height)."""
        return get_virtual_screen_bounds()

    @property
    def monitors(self) -> List[MonitorInfo]:
        """Lists all connected physical displays."""
        return get_monitors()

    @property
    def active_desktop(self) -> str:
        """Returns active desktop name (e.g. 'Default', 'Winlogon')."""
        return get_active_desktop_name()

    @property
    def is_secure_desktop(self) -> bool:
        """Returns True if the OS has switched to a secure desktop (UAC, Lock Screen)."""
        return is_secure_desktop_active()

    @property
    def is_uac_prompt_active(self) -> bool:
        """Returns True if Windows User Account Control (UAC) prompt is currently waiting."""
        return is_uac_active()

    @property
    def ocr_languages(self) -> List[str]:
        """Lists available Windows OCR languages."""
        return get_available_languages()

    @property
    def trace_history(self) -> List[ActionRecord]:
        """Returns recorded action history if tracing is enabled."""
        return self.tracer.history

    def enable_tracing(self, debug_dir: Optional[str] = None):
        """Enables visual step recording with annotated screenshots."""
        self.tracer.enable(output_dir=debug_dir)

    def disable_tracing(self):
        """Disables visual step recording."""
        self.tracer.disable()

    # --- Window Management & Geometry ---

    def list_windows(self, visible_only: bool = True) -> List[WindowInfo]:
        """Lists active windows with title and coordinates."""
        return list_windows(visible_only=visible_only)

    def find_window(self, query: str) -> Optional[WindowInfo]:
        """Finds first window matching the query."""
        return find_window(query)

    def find_windows(self, query: str) -> List[WindowInfo]:
        """Finds all windows matching the query."""
        return find_windows(query)

    def focus(self, window: Union[str, WindowInfo, int]) -> bool:
        """Brings the window to the front with anti-lockout protection."""
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

    def resize_window(self, window: Union[str, WindowInfo, int], width: int, height: int) -> bool:
        """Resizes the window."""
        return resize_window(window, width, height)

    def move_window(self, window: Union[str, WindowInfo, int], x: int, y: int) -> bool:
        """Moves the window."""
        return move_window(window, x, y)

    def center_window(self, window: Union[str, WindowInfo, int], monitor_index: int = 0) -> bool:
        """Centers the window on the specified display."""
        return center_window(window, monitor_index=monitor_index)

    def maximize_window(self, window: Union[str, WindowInfo, int]) -> bool:
        """Maximizes the window."""
        return maximize_window(window)

    def minimize_window(self, window: Union[str, WindowInfo, int]) -> bool:
        """Minimizes the window."""
        return minimize_window(window)

    def close_window(self, window: Union[str, WindowInfo, int], force: bool = False) -> bool:
        """Closes the window."""
        return close_window(window, force=force)

    # --- Application Lifecycle ---

    def launch_app(
        self,
        command_or_path: Union[str, List[str]],
        wait_window_query: Optional[str] = None,
        timeout: float = 10.0,
    ) -> Tuple[subprocess.Popen, Optional[WindowInfo]]:
        """Spawns an application and optionally waits for its window."""
        return launch_app(command_or_path, wait_window_query=wait_window_query, timeout=timeout)

    def terminate_process(self, name_or_pid: Union[str, int], force: bool = True) -> bool:
        """Terminates an application process."""
        return terminate_process(name_or_pid, force=force)

    def is_process_running(self, name_or_pid: Union[str, int]) -> bool:
        """Checks if a process is alive."""
        return is_process_running(name_or_pid)

    # --- Smart Waiting & Synchronization ---

    def wait_for_window(self, title_query: str, timeout: float = 10.0, interval: float = 0.5) -> Optional[WindowInfo]:
        """Waits for window to appear."""
        return wait_for_window(title_query, timeout=timeout, interval=interval)

    def wait_for_text(
        self,
        query: str,
        window: Optional[Union[str, WindowInfo, int]] = None,
        timeout: float = 10.0,
        interval: float = 0.5,
        lang: Optional[str] = None,
    ) -> bool:
        """Waits for text to appear on screen/window."""
        return wait_for_text(query, window=window, timeout=timeout, interval=interval, lang=lang)

    def wait_for_element(
        self,
        window: Union[str, WindowInfo, int],
        name: Optional[str] = None,
        control_type: Optional[str] = None,
        timeout: float = 10.0,
        interval: float = 0.5,
    ) -> bool:
        """Waits for UI automation element to appear."""
        return wait_for_element(window, name=name, control_type=control_type, timeout=timeout, interval=interval)

    def wait_for_change(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        window: Optional[Union[str, WindowInfo, int]] = None,
        timeout: float = 5.0,
        interval: float = 0.2,
    ) -> bool:
        """Waits until screen/window pixels change."""
        return wait_for_change(region=region, window=window, timeout=timeout, interval=interval)

    def wait_until_idle(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        window: Optional[Union[str, WindowInfo, int]] = None,
        timeout: float = 10.0,
        settle_time: float = 0.5,
    ) -> bool:
        """Waits until screen/window stops changing for at least settle_time seconds."""
        return wait_until_idle(region=region, window=window, timeout=timeout, settle_time=settle_time)

    # --- Perception / Vision ---

    def capture(
        self,
        output_path: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        all_monitors: bool = False,
        monitor_index: Optional[int] = None,
    ) -> Image.Image:
        """Captures the screen, specific monitor, or bounding region."""
        img = capture_screen(
            region=region,
            all_monitors=all_monitors,
            monitor_index=monitor_index,
        )
        if output_path:
            save_capture(img, output_path)
        return img

    def capture_all(self, output_path: Optional[str] = None) -> Image.Image:
        """Captures the full multi-monitor virtual desktop."""
        return self.capture(output_path=output_path, all_monitors=True)

    def capture_monitor(self, monitor_index: int = 0, output_path: Optional[str] = None) -> Image.Image:
        """Captures a specific physical monitor by index."""
        return self.capture(output_path=output_path, monitor_index=monitor_index)

    def capture_window(
        self,
        window: Union[str, WindowInfo, int],
        output_path: Optional[str] = None,
        focus: bool = True,
    ) -> Tuple[Image.Image, WindowInfo]:
        """Brings target window to focus and captures it."""
        img, win = capture_window(window, focus=focus)
        if output_path:
            save_capture(img, output_path)
        return img, win

    # --- UI Automation (UIA) ---

    def inspect_elements(
        self,
        window: Union[str, WindowInfo, int],
        max_depth: int = 4,
    ) -> List[UIElement]:
        """Inspects native UI elements in target window."""
        return inspect_elements(window, max_depth=max_depth)

    def find_element(
        self,
        window: Union[str, WindowInfo, int],
        name: Optional[str] = None,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
    ) -> Optional[UIElement]:
        """Finds first native UI element matching criteria."""
        return find_element(
            window,
            name=name,
            control_type=control_type,
            automation_id=automation_id,
        )

    def click_element(
        self,
        window: Union[str, WindowInfo, int],
        name: Optional[str] = None,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        invoke_directly: bool = True,
    ) -> bool:
        """Clicks or programmatically invokes a native UI element."""
        el = self.find_element(window, name=name, control_type=control_type, automation_id=automation_id)
        if el and self.tracer.enabled:
            self.tracer.record_action("click_element", el.center, {"name": name, "type": control_type})
        return click_element(
            window,
            name=name,
            control_type=control_type,
            automation_id=automation_id,
            invoke_directly=invoke_directly,
        )

    def set_element_text(
        self,
        window: Union[str, WindowInfo, int],
        text: str,
        name: Optional[str] = None,
        automation_id: Optional[str] = None,
    ) -> bool:
        """Sets the text value of an input or edit UI element."""
        return set_element_text(
            window,
            text=text,
            name=name,
            automation_id=automation_id,
        )

    # --- Local Offline OCR ---

    def read_text(
        self,
        window: Optional[Union[str, WindowInfo, int]] = None,
        image: Optional[Image.Image] = None,
        lang: Optional[str] = None,
    ) -> str:
        """Extracts text from screen, window, or image using Windows OCR."""
        if image is None:
            if window is not None:
                image, _ = self.capture_window(window, focus=True)
            else:
                image = self.capture(all_monitors=True)
        res = recognize_text(image, lang=lang)
        return res.get("text", "")

    def find_text(
        self,
        query: str,
        window: Optional[Union[str, WindowInfo, int]] = None,
        exact: bool = False,
        lang: Optional[str] = None,
    ) -> List[TextMatch]:
        """Finds on-screen or window text with bounding boxes."""
        return find_text(query, window=window, exact=exact, lang=lang)

    def click_text(
        self,
        query: str,
        window: Optional[Union[str, WindowInfo, int]] = None,
        exact: bool = False,
        lang: Optional[str] = None,
    ) -> Optional[Tuple[int, int]]:
        """Finds text and clicks its center coordinate."""
        pt = click_text(query, window=window, exact=exact, lang=lang)
        if pt and self.tracer.enabled:
            self.tracer.record_action("click_text", pt, {"query": query})
        return pt

    # --- Action / Interaction ---

    def hover(self, x: int, y: int, duration: float = 0.2):
        """Hovers mouse over (x, y)."""
        hover(x, y, duration=duration)
        if self.tracer.enabled:
            self.tracer.record_action("hover", (x, y))

    def hover_window(
        self,
        window: Union[str, WindowInfo, int],
        rel_x: float = 0.5,
        rel_y: float = 0.5,
    ) -> Tuple[int, int]:
        """Hovers relative to target window."""
        pt = hover_window(window, rel_x=rel_x, rel_y=rel_y)
        if self.tracer.enabled:
            self.tracer.record_action("hover_window", pt, {"rel_x": rel_x, "rel_y": rel_y})
        return pt

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left"):
        """Clicks at (x, y)."""
        click(x=x, y=y, button=button)
        if x is not None and y is not None and self.tracer.enabled:
            self.tracer.record_action(f"click_{button}", (x, y))

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """Double clicks at (x, y)."""
        double_click(x=x, y=y)
        if x is not None and y is not None and self.tracer.enabled:
            self.tracer.record_action("double_click", (x, y))

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """Right clicks at (x, y)."""
        right_click(x=x, y=y)
        if x is not None and y is not None and self.tracer.enabled:
            self.tracer.record_action("right_click", (x, y))

    def click_window(
        self,
        window: Union[str, WindowInfo, int],
        rel_x: float = 0.5,
        rel_y: float = 0.5,
        button: str = "left",
    ) -> Tuple[int, int]:
        """Clicks relative to the target window (0.5, 0.5 is center)."""
        pt = click_window(window, rel_x=rel_x, rel_y=rel_y, button=button)
        if self.tracer.enabled:
            self.tracer.record_action(f"click_window_{button}", pt, {"rel_x": rel_x, "rel_y": rel_y})
        return pt

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        button: str = "left",
    ):
        """Drags mouse from start to end coordinates."""
        drag_and_drop(start_x, start_y, end_x, end_y, duration=duration, button=button)
        if self.tracer.enabled:
            self.tracer.record_action("drag_and_drop", (end_x, end_y), {"start": (start_x, start_y)})

    def drag_to(self, x: int, y: int, duration: float = 0.5, button: str = "left"):
        """Drags mouse from current position to (x, y)."""
        drag_to(x, y, duration=duration, button=button)
        if self.tracer.enabled:
            self.tracer.record_action("drag_to", (x, y))

    def scroll_down(self, amount: int = 500, x: Optional[int] = None, y: Optional[int] = None):
        """Scrolls down."""
        scroll(-abs(amount), x=x, y=y)

    def scroll_up(self, amount: int = 500, x: Optional[int] = None, y: Optional[int] = None):
        """Scrolls up."""
        scroll(abs(amount), x=x, y=y)

    def type(self, text: str, interval: float = 0.02, use_clipboard_fallback: bool = True):
        """Types text on keyboard. Uses clipboard paste automatically for Turkish/Unicode."""
        type_text(text, interval=interval, use_clipboard_fallback=use_clipboard_fallback)
        if self.tracer.enabled:
            self.tracer.record_action("type", details={"text": text}, annotate=False)

    def paste(self, text: str, restore_clipboard: bool = False):
        """Pastes text via system clipboard and Ctrl+V."""
        paste_text(text, restore_clipboard=restore_clipboard)
        if self.tracer.enabled:
            self.tracer.record_action("paste", details={"text": text}, annotate=False)

    def press(self, key: str):
        """Presses a key."""
        press_key(key)

    def hotkey(self, *keys: str):
        """Presses keyboard shortcut combinations."""
        hotkey(*keys)

    def wait(self, seconds: float):
        """Pauses execution."""
        time.sleep(seconds)
