"""
Example: Live Feed Reader & Content Perception
Demonstrates focusing a browser window, scrolling content, and capturing visual frames.
"""

import time
from desktop_vision import DesktopAgent


def main():
    agent = DesktopAgent()

    # 1. Search for a web browser window
    browser_win = None
    for name in ["Brave", "Chrome", "Firefox", "Edge"]:
        browser_win = agent.find_window(name)
        if browser_win:
            break

    if not browser_win:
        print("No browser window found.")
        return

    print(f"Targeting browser window: '{browser_win.title}'")
    agent.focus(browser_win)
    time.sleep(0.5)

    # 2. Capture initial frame
    print("Capturing Frame 1...")
    agent.capture_window(browser_win, output_path="feed_frame_1.png")

    # 3. Scroll down to next content item
    print("Scrolling down...")
    agent.click_window(browser_win, rel_x=0.5, rel_y=0.5)
    agent.scroll_down(800)
    time.sleep(2.0)

    # 4. Capture second frame
    print("Capturing Frame 2...")
    agent.capture_window(browser_win, output_path="feed_frame_2.png")

    print("[SUCCESS] Frames captured for multimodal inspection.")


if __name__ == "__main__":
    main()
