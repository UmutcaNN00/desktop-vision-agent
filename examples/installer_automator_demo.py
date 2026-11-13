"""
Example: Automated GUI Installer Navigation
Demonstrates how an AI agent uses Desktop Vision to automate GUI installers (e.g. Inno Setup, NSIS, MSI).
"""

import time
from desktop_vision import DesktopAgent


def main():
    agent = DesktopAgent()
    print(f"Screen resolution: {agent.screen_size}")

    # 1. Search for an installer window
    print("Searching for setup / installer window...")
    setup_win = agent.find_window("setup")
    if not setup_win:
        print("No active setup window found. Listing all active windows:")
        for w in agent.list_windows()[:5]:
            print(f"  - [{w.hwnd}] {w.title}")
        return

    print(f"Found setup window: '{setup_win.title}' (HWND: {setup_win.hwnd})")

    # 2. Focus and take a snapshot for the agent's vision model
    agent.focus(setup_win)
    img, win = agent.capture_window(setup_win, output_path="setup_current_step.png")
    print(f"Captured window snapshot ({win.width}x{win.height}) to setup_current_step.png")

    # 3. Simulate clicking the primary action button (e.g., Next / Install / Enter)
    print("Advancing setup (pressing Enter)...")
    agent.press("enter")
    time.sleep(1.5)

    # 4. Capture after action to verify progression
    agent.capture_window(setup_win, output_path="setup_next_step.png")
    print("Verification capture saved to setup_next_step.png")


if __name__ == "__main__":
    main()
