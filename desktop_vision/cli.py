"""
Desktop Vision CLI (v0.3.0)
Command-line interface for human users and AI agents to observe, inspect, and control Windows OS.
"""

import argparse
import sys
from .agent import DesktopAgent


def main():
    parser = argparse.ArgumentParser(
        prog="desktop-vision",
        description="Autonomous Desktop Perception, UI Automation, Native OCR & OS Control Engine for AI Agents",
    )
    parser.add_argument("--trace", nargs="?", const=".debug", default=None, help="Enable visual action tracing to directory (default: .debug)")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Display & Windows
    subparsers.add_parser("list-windows", help="List all visible windows with titles and coordinates")
    subparsers.add_parser("list-monitors", help="List all connected physical displays")

    focus_parser = subparsers.add_parser("focus", help="Bring a window to the foreground")
    focus_parser.add_argument("window", help="Title substring of the window to focus")

    move_parser = subparsers.add_parser("move-window", help="Move window to (x, y)")
    move_parser.add_argument("window", help="Title substring of window")
    move_parser.add_argument("x", type=int, help="X coordinate")
    move_parser.add_argument("y", type=int, help="Y coordinate")

    resize_parser = subparsers.add_parser("resize-window", help="Resize window to width x height")
    resize_parser.add_argument("window", help="Title substring of window")
    resize_parser.add_argument("width", type=int, help="Width in pixels")
    resize_parser.add_argument("height", type=int, help="Height in pixels")

    center_parser = subparsers.add_parser("center-window", help="Center window on monitor")
    center_parser.add_argument("window", help="Title substring of window")
    center_parser.add_argument("--monitor", type=int, default=0, help="Monitor index (default: 0)")

    max_parser = subparsers.add_parser("maximize-window", help="Maximize window")
    max_parser.add_argument("window", help="Title substring of window")

    min_parser = subparsers.add_parser("minimize-window", help="Minimize window")
    min_parser.add_argument("window", help="Title substring of window")

    close_parser = subparsers.add_parser("close-window", help="Close window gracefully or forcefully")
    close_parser.add_argument("window", help="Title substring of window")
    close_parser.add_argument("--force", action="store_true", help="Force terminate process")

    # Visual Capture
    cap_parser = subparsers.add_parser("capture", help="Take a screen capture")
    cap_parser.add_argument("-o", "--output", default="screenshot.png", help="Path to save the screenshot")
    cap_parser.add_argument("--all", action="store_true", help="Capture across all monitors (virtual desktop)")
    cap_parser.add_argument("--monitor", type=int, default=None, help="Capture specific monitor index (0, 1, ...)")

    capw_parser = subparsers.add_parser("capture-window", help="Focus and capture a specific window")
    capw_parser.add_argument("window", help="Title substring of the window")
    capw_parser.add_argument("-o", "--output", default="window.png", help="Path to save the screenshot")

    # Mouse & Keyboard Actions
    click_parser = subparsers.add_parser("click", help="Click mouse at (x, y)")
    click_parser.add_argument("x", type=int, help="X coordinate")
    click_parser.add_argument("y", type=int, help="Y coordinate")
    click_parser.add_argument("--button", default="left", choices=["left", "right", "middle"], help="Mouse button")

    clickw_parser = subparsers.add_parser("click-window", help="Click relative coordinates inside a window")
    clickw_parser.add_argument("window", help="Title substring of the window")
    clickw_parser.add_argument("--rx", type=float, default=0.5, help="Relative X (0.0 to 1.0, default 0.5 center)")
    clickw_parser.add_argument("--ry", type=float, default=0.5, help="Relative Y (0.0 to 1.0, default 0.5 center)")

    hover_parser = subparsers.add_parser("hover", help="Hover mouse at (x, y)")
    hover_parser.add_argument("x", type=int, help="X coordinate")
    hover_parser.add_argument("y", type=int, help="Y coordinate")

    hoverw_parser = subparsers.add_parser("hover-window", help="Hover mouse relative inside window")
    hoverw_parser.add_argument("window", help="Title substring of window")
    hoverw_parser.add_argument("--rx", type=float, default=0.5, help="Relative X (default 0.5)")
    hoverw_parser.add_argument("--ry", type=float, default=0.5, help="Relative Y (default 0.5)")

    drag_parser = subparsers.add_parser("drag", help="Drag mouse from (x1, y1) to (x2, y2)")
    drag_parser.add_argument("start_x", type=int, help="Start X")
    drag_parser.add_argument("start_y", type=int, help="Start Y")
    drag_parser.add_argument("end_x", type=int, help="End X")
    drag_parser.add_argument("end_y", type=int, help="End Y")

    scroll_parser = subparsers.add_parser("scroll", help="Scroll mouse wheel")
    scroll_parser.add_argument("amount", type=int, help="Scroll units (negative=down, positive=up)")
    scroll_parser.add_argument("--x", type=int, default=None, help="Target X coordinate")
    scroll_parser.add_argument("--y", type=int, default=None, help="Target Y coordinate")

    type_parser = subparsers.add_parser("type", help="Type text via keyboard (with clipboard Unicode support)")
    type_parser.add_argument("text", help="Text string to type")
    type_parser.add_argument("--interval", type=float, default=0.02, help="Delay between keystrokes")

    paste_parser = subparsers.add_parser("paste", help="Paste text via clipboard and Ctrl+V")
    paste_parser.add_argument("text", help="Text string to paste")

    press_parser = subparsers.add_parser("press", help="Press a keyboard key")
    press_parser.add_argument("key", help="Key name (e.g. enter, tab, esc, pagedown)")

    hotkey_parser = subparsers.add_parser("hotkey", help="Press a combination of keys")
    hotkey_parser.add_argument("keys", nargs="+", help="Keys to press simultaneously (e.g. ctrl shift esc)")

    # UI Automation (UIA)
    elem_parser = subparsers.add_parser("inspect-elements", help="Inspect native UI element hierarchy")
    elem_parser.add_argument("window", help="Title substring of the window")
    elem_parser.add_argument("--depth", type=int, default=4, help="Maximum hierarchy tree depth")

    clkel_parser = subparsers.add_parser("click-element", help="Click/invoke a UI element inside a window")
    clkel_parser.add_argument("window", help="Title substring of the window")
    clkel_parser.add_argument("--name", default=None, help="Control name / label")
    clkel_parser.add_argument("--type", default=None, help="Control type (Button, Edit, CheckBox, etc.)")
    clkel_parser.add_argument("--id", default=None, help="Automation ID")

    # Local OCR
    ocr_parser = subparsers.add_parser("ocr", help="Perform offline OCR on screen or window")
    ocr_parser.add_argument("--window", default=None, help="Title substring of window (default: all screens)")
    ocr_parser.add_argument("--lang", default=None, help="Preferred OCR language (e.g. tr, en)")

    clktxt_parser = subparsers.add_parser("click-text", help="Find text with OCR and click its center")
    clktxt_parser.add_argument("text", help="Text query to find and click")
    clktxt_parser.add_argument("--window", default=None, help="Limit search to window")
    clktxt_parser.add_argument("--exact", action="store_true", help="Match exact text only")
    clktxt_parser.add_argument("--lang", default=None, help="Preferred OCR language")

    # Process Lifecycle & Synchronization
    launch_parser = subparsers.add_parser("launch", help="Launch an application and optionally wait for window")
    launch_parser.add_argument("command", help="Command or path to executable")
    launch_parser.add_argument("--wait-window", default=None, help="Window title substring to wait for")
    launch_parser.add_argument("--timeout", type=float, default=10.0, help="Wait timeout in seconds")

    term_parser = subparsers.add_parser("terminate", help="Terminate a process by name or PID")
    term_parser.add_argument("target", help="Process name (e.g. notepad.exe) or PID")
    term_parser.add_argument("--force", action="store_true", default=True, help="Force kill")

    waitw_parser = subparsers.add_parser("wait-window", help="Wait until window appears")
    waitw_parser.add_argument("title", help="Window title substring to wait for")
    waitw_parser.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")

    waitt_parser = subparsers.add_parser("wait-text", help="Wait until text appears via OCR")
    waitt_parser.add_argument("text", help="Text query to wait for")
    waitt_parser.add_argument("--window", default=None, help="Target window")
    waitt_parser.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")

    idle_parser = subparsers.add_parser("wait-idle", help="Wait until screen/window stops changing")
    idle_parser.add_argument("--window", default=None, help="Target window")
    idle_parser.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")

    subparsers.add_parser("check-uac", help="Check if Windows UAC or secure desktop is active")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    agent = DesktopAgent(enable_tracing=bool(args.trace), debug_dir=args.trace or ".debug")

    # Command Execution
    if args.command == "list-windows":
        wins = agent.list_windows()
        print(f"--- Found {len(wins)} Active Windows ---")
        for w in wins:
            print(f"[{w.hwnd}] '{w.title}' -> Rect: ({w.left}, {w.top}, {w.right}, {w.bottom}) Size: {w.width}x{w.height}")

    elif args.command == "list-monitors":
        mons = agent.monitors
        print(f"--- Found {len(mons)} Displays (Virtual Desktop: {agent.virtual_screen_bounds}) ---")
        for m in mons:
            pri = " [Primary]" if m.is_primary else ""
            print(f"Monitor {m.index}: {m.device}{pri} -> Rect: {m.rect} ({m.width}x{m.height})")

    elif args.command == "focus":
        ok = agent.focus(args.window)
        if ok:
            print(f"[OK] Focused window matching '{args.window}'")
        else:
            print(f"[ERROR] Could not find or focus window matching '{args.window}'")
            sys.exit(1)

    elif args.command == "move-window":
        ok = agent.move_window(args.window, args.x, args.y)
        print(f"[{'OK' if ok else 'ERROR'}] Move window '{args.window}' to ({args.x}, {args.y})")

    elif args.command == "resize-window":
        ok = agent.resize_window(args.window, args.width, args.height)
        print(f"[{'OK' if ok else 'ERROR'}] Resize window '{args.window}' to {args.width}x{args.height}")

    elif args.command == "center-window":
        ok = agent.center_window(args.window, monitor_index=args.monitor)
        print(f"[{'OK' if ok else 'ERROR'}] Centered window '{args.window}' on monitor {args.monitor}")

    elif args.command == "maximize-window":
        ok = agent.maximize_window(args.window)
        print(f"[{'OK' if ok else 'ERROR'}] Maximized window '{args.window}'")

    elif args.command == "minimize-window":
        ok = agent.minimize_window(args.window)
        print(f"[{'OK' if ok else 'ERROR'}] Minimized window '{args.window}'")

    elif args.command == "close-window":
        ok = agent.close_window(args.window, force=args.force)
        print(f"[{'OK' if ok else 'ERROR'}] Closed window '{args.window}' (force={args.force})")

    elif args.command == "capture":
        agent.capture(
            output_path=args.output,
            all_monitors=args.all,
            monitor_index=args.monitor,
        )
        print(f"[OK] Screenshot saved to: {args.output}")

    elif args.command == "capture-window":
        try:
            _, win = agent.capture_window(args.window, output_path=args.output)
            print(f"[OK] Captured window '{win.title}' (HWND: {win.hwnd}) to: {args.output}")
        except Exception as e:
            print(f"[ERROR] Failed to capture window: {e}")
            sys.exit(1)

    elif args.command == "click":
        agent.click(args.x, args.y, button=args.button)
        print(f"[OK] Clicked at ({args.x}, {args.y}) with {args.button} button")

    elif args.command == "click-window":
        try:
            x, y = agent.click_window(args.window, rel_x=args.rx, rel_y=args.ry)
            print(f"[OK] Clicked relative ({args.rx}, {args.ry}) inside '{args.window}' -> Screen ({x}, {y})")
        except Exception as e:
            print(f"[ERROR] Failed to click window: {e}")
            sys.exit(1)

    elif args.command == "hover":
        agent.hover(args.x, args.y)
        print(f"[OK] Hovered at ({args.x}, {args.y})")

    elif args.command == "hover-window":
        x, y = agent.hover_window(args.window, rel_x=args.rx, rel_y=args.ry)
        print(f"[OK] Hovered relative ({args.rx}, {args.ry}) inside '{args.window}' -> ({x}, {y})")

    elif args.command == "drag":
        agent.drag(args.start_x, args.start_y, args.end_x, args.end_y)
        print(f"[OK] Dragged from ({args.start_x}, {args.start_y}) to ({args.end_x}, {args.end_y})")

    elif args.command == "scroll":
        agent.scroll_down(-args.amount, x=args.x, y=args.y)
        print(f"[OK] Scrolled {args.amount} units")

    elif args.command == "type":
        agent.type(args.text, interval=args.interval)
        print(f"[OK] Typed text: {args.text}")

    elif args.command == "paste":
        agent.paste(args.text)
        print(f"[OK] Pasted text via clipboard: {args.text}")

    elif args.command == "press":
        agent.press(args.key)
        print(f"[OK] Pressed key: {args.key}")

    elif args.command == "hotkey":
        agent.hotkey(*args.keys)
        print(f"[OK] Pressed hotkey: {'+'.join(args.keys)}")

    elif args.command == "inspect-elements":
        try:
            elems = agent.inspect_elements(args.window, max_depth=args.depth)
            print(f"--- Found {len(elems)} UI Elements in '{args.window}' (Depth <= {args.depth}) ---")
            for el in elems:
                print(str(el))
        except Exception as e:
            print(f"[ERROR] Failed to inspect elements: {e}")
            sys.exit(1)

    elif args.command == "click-element":
        ok = agent.click_element(
            args.window,
            name=args.name,
            control_type=args.type,
            automation_id=args.id,
        )
        if ok:
            print(f"[OK] Clicked/Invoked element in '{args.window}'")
        else:
            print(f"[ERROR] Element matching criteria not found in '{args.window}'")
            sys.exit(1)

    elif args.command == "ocr":
        try:
            text = agent.read_text(window=args.window, lang=args.lang)
            print("--- OCR Extracted Text ---")
            print(text.strip() if text else "<No text detected>")
        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
            sys.exit(1)

    elif args.command == "click-text":
        pt = agent.click_text(args.text, window=args.window, exact=args.exact, lang=args.lang)
        if pt:
            print(f"[OK] Found and clicked text '{args.text}' at screen coords: {pt}")
        else:
            print(f"[ERROR] Text '{args.text}' not found")
            sys.exit(1)

    elif args.command == "launch":
        proc, win = agent.launch_app(args.command, wait_window_query=args.wait_window, timeout=args.timeout)
        print(f"[OK] Launched process PID {proc.pid}")
        if win:
            print(f"[OK] Window appeared: '{win.title}' (HWND: {win.hwnd})")

    elif args.command == "terminate":
        target = int(args.target) if args.target.isdigit() else args.target
        ok = agent.terminate_process(target, force=args.force)
        print(f"[{'OK' if ok else 'ERROR'}] Terminated target {target}")

    elif args.command == "wait-window":
        win = agent.wait_for_window(args.title, timeout=args.timeout)
        if win:
            print(f"[OK] Window appeared: '{win.title}' (HWND: {win.hwnd})")
        else:
            print(f"[ERROR] Timed out waiting for window matching '{args.title}'")
            sys.exit(1)

    elif args.command == "wait-text":
        ok = agent.wait_for_text(args.text, window=args.window, timeout=args.timeout)
        print(f"[{'OK' if ok else 'TIMEOUT'}] Text '{args.text}' found: {ok}")

    elif args.command == "wait-idle":
        ok = agent.wait_until_idle(window=args.window, timeout=args.timeout)
        print(f"[{'OK' if ok else 'TIMEOUT'}] Visual state settled: {ok}")

    elif args.command == "check-uac":
        print(f"Active Desktop: '{agent.active_desktop}'")
        print(f"Is Secure Desktop: {agent.is_secure_desktop}")
        print(f"Is UAC Prompt Waiting: {agent.is_uac_prompt_active}")


if __name__ == "__main__":
    main()
