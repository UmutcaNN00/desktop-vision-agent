"""
Desktop Vision CLI
Command-line interface for human users and AI agents to observe and interact with the OS.
"""

import argparse
import sys
from .agent import DesktopAgent


def main():
    parser = argparse.ArgumentParser(
        prog="desktop-vision",
        description="Autonomous Desktop Perception and Control Engine for AI Agents"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: list-windows
    subparsers.add_parser("list-windows", help="List all visible windows with titles and coordinates")

    # Command: capture
    cap_parser = subparsers.add_parser("capture", help="Take a full screen capture")
    cap_parser.add_argument("-o", "--output", default="screenshot.png", help="Path to save the screenshot")

    # Command: capture-window
    capw_parser = subparsers.add_parser("capture-window", help="Focus and capture a specific window")
    capw_parser.add_argument("window", help="Title substring of the window")
    capw_parser.add_argument("-o", "--output", default="window.png", help="Path to save the screenshot")

    # Command: focus
    focus_parser = subparsers.add_parser("focus", help="Bring a window to the foreground")
    focus_parser.add_argument("window", help="Title substring of the window to focus")

    # Command: click
    click_parser = subparsers.add_parser("click", help="Click mouse at (x, y)")
    click_parser.add_argument("x", type=int, help="X coordinate")
    click_parser.add_argument("y", type=int, help="Y coordinate")
    click_parser.add_argument("--button", default="left", choices=["left", "right", "middle"], help="Mouse button")

    # Command: click-window
    clickw_parser = subparsers.add_parser("click-window", help="Click relative coordinates inside a window")
    clickw_parser.add_argument("window", help="Title substring of the window")
    clickw_parser.add_argument("--rx", type=float, default=0.5, help="Relative X (0.0 to 1.0, default 0.5 center)")
    clickw_parser.add_argument("--ry", type=float, default=0.5, help="Relative Y (0.0 to 1.0, default 0.5 center)")

    # Command: scroll
    scroll_parser = subparsers.add_parser("scroll", help="Scroll mouse wheel")
    scroll_parser.add_argument("amount", type=int, help="Scroll units (negative=down, positive=up)")
    scroll_parser.add_argument("--x", type=int, default=None, help="Target X coordinate")
    scroll_parser.add_argument("--y", type=int, default=None, help="Target Y coordinate")

    # Command: type
    type_parser = subparsers.add_parser("type", help="Type text via keyboard")
    type_parser.add_argument("text", help="Text string to type")
    type_parser.add_argument("--interval", type=float, default=0.02, help="Delay between keystrokes")

    # Command: press
    press_parser = subparsers.add_parser("press", help="Press a keyboard key")
    press_parser.add_argument("key", help="Key name (e.g. enter, tab, esc, pagedown)")

    # Command: hotkey
    hotkey_parser = subparsers.add_parser("hotkey", help="Press a combination of keys")
    hotkey_parser.add_argument("keys", nargs="+", help="Keys to press simultaneously (e.g. ctrl shift esc)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    agent = DesktopAgent()

    if args.command == "list-windows":
        wins = agent.list_windows()
        print(f"--- Found {len(wins)} Active Windows ---")
        for w in wins:
            print(f"[{w.hwnd}] '{w.title}' -> Rect: ({w.left}, {w.top}, {w.right}, {w.bottom}) Size: {w.width}x{w.height}")

    elif args.command == "capture":
        agent.capture(output_path=args.output)
        print(f"[OK] Full screenshot saved to: {args.output}")

    elif args.command == "capture-window":
        try:
            _, win = agent.capture_window(args.window, output_path=args.output)
            print(f"[OK] Captured window '{win.title}' (HWND: {win.hwnd}) to: {args.output}")
        except Exception as e:
            print(f"[ERROR] Failed to capture window: {e}")
            sys.exit(1)

    elif args.command == "focus":
        ok = agent.focus(args.window)
        if ok:
            print(f"[OK] Focused window matching '{args.window}'")
        else:
            print(f"[ERROR] Could not find or focus window matching '{args.window}'")
            sys.exit(1)

    elif args.command == "click":
        agent.click(args.x, args.y, button=args.button)
        print(f"[OK] Clicked at ({args.x}, {args.y}) with {args.button} button")

    elif args.command == "click-window":
        try:
            tx, ty = agent.click_window(args.window, rel_x=args.rx, rel_y=args.ry)
            print(f"[OK] Clicked inside '{args.window}' at relative ({args.rx}, {args.ry}) -> Screen ({tx}, {ty})")
        except Exception as e:
            print(f"[ERROR] {e}")
            sys.exit(1)

    elif args.command == "scroll":
        agent.scroll_up(args.amount, x=args.x, y=args.y) if args.amount > 0 else agent.scroll_down(abs(args.amount), x=args.x, y=args.y)
        print(f"[OK] Scrolled {args.amount} units")

    elif args.command == "type":
        agent.type(args.text, interval=args.interval)
        print(f"[OK] Typed text: {args.text}")

    elif args.command == "press":
        agent.press(args.key)
        print(f"[OK] Pressed key: {args.key}")

    elif args.command == "hotkey":
        agent.hotkey(*args.keys)
        print(f"[OK] Pressed hotkey: {' + '.join(args.keys)}")


if __name__ == "__main__":
    main()
