"""
Visual Action Tracing & Audit Trail Module
Records every agent action with step timestamps, JSONL logs, and annotated screenshots
featuring visual target markers (crosshairs & labels) for transparent debugging.
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw

from .capture import capture_screen


@dataclass
class ActionRecord:
    step: int
    timestamp: float
    action: str
    target_coords: Optional[Tuple[int, int]] = None
    details: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None


class ActionTracer:
    """
    Visual action audit tracer for AI agents.
    """

    def __init__(self, output_dir: str = ".debug", enabled: bool = False):
        self.output_dir = os.path.abspath(output_dir)
        self.enabled = enabled
        self.step_counter = 0
        self.history: List[ActionRecord] = []
        if self.enabled:
            os.makedirs(self.output_dir, exist_ok=True)

    def enable(self, output_dir: Optional[str] = None):
        """Enables visual action tracing."""
        if output_dir:
            self.output_dir = os.path.abspath(output_dir)
        self.enabled = True
        os.makedirs(self.output_dir, exist_ok=True)

    def disable(self):
        """Disables visual action tracing."""
        self.enabled = False

    def clear(self):
        """Resets the history and step counter."""
        self.step_counter = 0
        self.history.clear()

    def record_action(
        self,
        action: str,
        coords: Optional[Tuple[int, int]] = None,
        details: Optional[Dict[str, Any]] = None,
        annotate: bool = True,
    ) -> Optional[ActionRecord]:
        """
        Records an action step. Captures and annotates screenshot if coords are provided.
        """
        if not self.enabled:
            return None

        self.step_counter += 1
        ts = time.time()
        shot_path = None

        if annotate:
            try:
                # Capture current display state
                img = capture_screen(all_monitors=True)
                draw = ImageDraw.Draw(img)

                if coords:
                    x, y = coords
                    r = 16
                    color = "red"
                    if "hover" in action.lower():
                        color = "blue"
                    elif "drag" in action.lower():
                        color = "orange"
                    elif "type" in action.lower() or "paste" in action.lower():
                        color = "green"

                    # Draw outer circle and inner point
                    draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=3)
                    draw.line((x - r - 6, y, x + r + 6, y), fill=color, width=2)
                    draw.line((x, y - r - 6, x, y + r + 6), fill=color, width=2)

                    # Action label
                    label = f"#{self.step_counter}: {action.upper()} ({x}, {y})"
                    draw.text((x + r + 8, y - 8), label, fill=color)

                filename = f"step_{self.step_counter:03d}_{action.lower()}.png"
                shot_path = os.path.join(self.output_dir, filename)
                img.save(shot_path)
            except Exception:
                pass

        record = ActionRecord(
            step=self.step_counter,
            timestamp=ts,
            action=action,
            target_coords=coords,
            details=details,
            screenshot_path=shot_path,
        )
        self.history.append(record)

        # Append to JSONL log
        try:
            log_file = os.path.join(self.output_dir, "actions.jsonl")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        except Exception:
            pass

        return record
