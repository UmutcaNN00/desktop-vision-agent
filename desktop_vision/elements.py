"""
UI Automation & Element Tree Inspection Module
Enables deterministic inspection and programmatic interaction with native Windows UI elements
(Buttons, Input fields, Checkboxes, Menus, etc.) using Microsoft UI Automation (UIA).
"""

import re
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

try:
    import uiautomation as auto
except ImportError:
    auto = None

from .desktop import attach_desktop
from .input import click, hotkey, type_text
from .window import WindowInfo, bring_to_front, find_window


@dataclass
class UIElement:
    name: str
    control_type: str
    automation_id: str
    class_name: str
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    is_enabled: bool
    depth: int = 0

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

    def __str__(self) -> str:
        indent = "  " * self.depth
        text = f"\"{self.name}\"" if self.name else "<unnamed>"
        id_str = f" id='{self.automation_id}'" if self.automation_id else ""
        return f"{indent}[{self.control_type}] {text}{id_str} rect=({self.left},{self.top},{self.right},{self.bottom})"


def _ensure_auto():
    if auto is None:
        raise ImportError(
            "uiautomation is required for element inspection. Install it with: pip install uiautomation"
        )
    attach_desktop()


def get_window_control(window: Union[str, WindowInfo, int]) -> Optional["auto.Control"]:
    """Resolves a window identifier to a UIAutomation Control object."""
    _ensure_auto()
    hwnd = None
    if isinstance(window, int):
        hwnd = window
    elif isinstance(window, WindowInfo):
        hwnd = window.hwnd
    elif isinstance(window, str):
        win_info = find_window(window)
        if win_info:
            hwnd = win_info.hwnd
        else:
            # Fallback to direct search via UIA WindowControl
            ctrl = auto.WindowControl(searchDepth=2, SubName=window)
            if ctrl.Exists(maxSearchSeconds=0.5):
                return ctrl
            return None

    if hwnd:
        return auto.ControlFromHandle(hwnd)
    return None


def inspect_elements(
    window: Union[str, WindowInfo, int],
    max_depth: int = 4,
    filter_empty: bool = True
) -> List[UIElement]:
    """
    Recursively inspects the UI element hierarchy of the specified window.
    """
    _ensure_auto()
    root_ctrl = get_window_control(window)
    if not root_ctrl:
        raise ValueError(f"Could not find or inspect window: {window}")

    elements: List[UIElement] = []

    def walk(ctrl: "auto.Control", depth: int):
        if depth > max_depth:
            return

        name = ctrl.Name or ""
        auto_id = ctrl.AutomationId or ""
        ctrl_type = ctrl.ControlTypeName or ""
        cls_name = ctrl.ClassName or ""
        r = ctrl.BoundingRectangle
        rect = (r.left, r.top, r.right, r.bottom)
        is_enabled = bool(ctrl.IsEnabled)

        # Include if has name/id or not filtering
        if not filter_empty or name or auto_id or (ctrl_type and ctrl_type != "PaneControl"):
            elem = UIElement(
                name=name.strip(),
                control_type=ctrl_type,
                automation_id=auto_id.strip(),
                class_name=cls_name,
                rect=rect,
                is_enabled=is_enabled,
                depth=depth,
            )
            elements.append(elem)

        for child in ctrl.GetChildren():
            walk(child, depth + 1)

    walk(root_ctrl, depth=0)
    return elements


def find_elements(
    window: Union[str, WindowInfo, int],
    name: Optional[str] = None,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None,
    exact: bool = False,
    max_depth: int = 5,
) -> List[UIElement]:
    """Finds all UI elements matching the given criteria."""
    all_elems = inspect_elements(window, max_depth=max_depth, filter_empty=False)
    matches = []

    name_re = None
    if name is not None:
        pat = f"^{re.escape(name)}$" if exact else re.escape(name)
        name_re = re.compile(pat, re.IGNORECASE)

    id_re = None
    if automation_id is not None:
        pat = f"^{re.escape(automation_id)}$" if exact else re.escape(automation_id)
        id_re = re.compile(pat, re.IGNORECASE)

    target_type = control_type.lower() if control_type else None

    for el in all_elems:
        if name_re and not name_re.search(el.name):
            continue
        if id_re and not id_re.search(el.automation_id):
            continue
        if target_type:
            actual_type = el.control_type.lower()
            if target_type not in actual_type:
                continue
        matches.append(el)

    return matches


def find_element(
    window: Union[str, WindowInfo, int],
    name: Optional[str] = None,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None,
    exact: bool = False,
    max_depth: int = 5,
) -> Optional[UIElement]:
    """Finds the first UI element matching the criteria."""
    matches = find_elements(
        window,
        name=name,
        control_type=control_type,
        automation_id=automation_id,
        exact=exact,
        max_depth=max_depth,
    )
    return matches[0] if matches else None


def click_element(
    window: Union[str, WindowInfo, int],
    name: Optional[str] = None,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None,
    invoke_directly: bool = True,
    focus: bool = True,
) -> bool:
    """
    Clicks or invokes a target UI element inside a window.
    Attempts direct UIA programmatic invocation first (works even when occluded),
    falling back to physical mouse clicks on the element center.
    """
    _ensure_auto()
    root_ctrl = get_window_control(window)
    if not root_ctrl:
        return False

    if focus:
        hwnd = root_ctrl.NativeWindowHandle
        if hwnd:
            bring_to_front(hwnd)
            time.sleep(0.15)

    elem = find_element(
        window,
        name=name,
        control_type=control_type,
        automation_id=automation_id,
    )
    if not elem:
        return False

    # Try direct programmatic invocation if requested
    if invoke_directly:
        try:
            # Re-locate actual UIA Control to invoke
            ctrl = None
            if elem.automation_id:
                ctrl = root_ctrl.Control(searchDepth=5, AutomationId=elem.automation_id)
            elif elem.name:
                ctrl = root_ctrl.Control(searchDepth=5, SubName=elem.name)

            if ctrl and ctrl.Exists(maxSearchSeconds=0.5):
                # Try InvokePattern
                try:
                    inv = ctrl.GetInvokePattern()
                    if inv:
                        inv.Invoke()
                        return True
                except Exception:
                    pass

                # Try TogglePattern (checkboxes, radiobuttons)
                try:
                    tog = ctrl.GetTogglePattern()
                    if tog:
                        tog.Toggle()
                        return True
                except Exception:
                    pass
        except Exception:
            pass

    # Physical mouse click fallback
    cx, cy = elem.center
    click(cx, cy)
    return True


def set_element_text(
    window: Union[str, WindowInfo, int],
    text: str,
    name: Optional[str] = None,
    automation_id: Optional[str] = None,
    clear_first: bool = True,
    focus: bool = True,
) -> bool:
    """
    Sets text of an edit control via ValuePattern or physical keystroke simulation.
    """
    _ensure_auto()
    root_ctrl = get_window_control(window)
    if not root_ctrl:
        return False

    if focus:
        hwnd = root_ctrl.NativeWindowHandle
        if hwnd:
            bring_to_front(hwnd)
            time.sleep(0.15)

    elem = find_element(
        window,
        name=name,
        control_type="Edit",
        automation_id=automation_id,
    )
    if not elem:
        # Fallback to any element matching name/id
        elem = find_element(window, name=name, automation_id=automation_id)

    if not elem:
        return False

    # Try ValuePattern directly
    try:
        ctrl = None
        if elem.automation_id:
            ctrl = root_ctrl.Control(searchDepth=5, AutomationId=elem.automation_id)
        elif elem.name:
            ctrl = root_ctrl.Control(searchDepth=5, SubName=elem.name)

        if ctrl and ctrl.Exists(0.5):
            val_pat = ctrl.GetValuePattern()
            if val_pat:
                val_pat.SetValue(text)
                return True
    except Exception:
        pass

    # Fallback to click + type
    cx, cy = elem.center
    click(cx, cy)
    time.sleep(0.1)
    if clear_first:
        hotkey("ctrl", "a")
        time.sleep(0.05)
    type_text(text)
    return True
