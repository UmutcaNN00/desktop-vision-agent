"""
Local Offline OCR Module
Performs high-speed, zero-token text recognition and text-based clicking using
the native Windows Media OCR runtime (winocr).
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image

try:
    import winocr
    from winocr import OcrEngine
except ImportError:
    winocr = None
    OcrEngine = None

from .capture import capture_screen, capture_window
from .desktop import attach_desktop, set_dpi_awareness
from .input import click
from .window import WindowInfo


@dataclass
class TextMatch:
    text: str
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    confidence: float = 1.0

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
        return f"\"{self.text}\" at ({self.left}, {self.top}, {self.right}, {self.bottom}) center=({self.center[0]}, {self.center[1]})"


def get_available_languages() -> List[str]:
    """Returns available Windows OCR language tags."""
    if not OcrEngine:
        return []
    try:
        return [lang.language_tag for lang in OcrEngine.available_recognizer_languages]
    except Exception:
        return []


def _resolve_language(preferred_lang: Optional[str] = None) -> str:
    avail = get_available_languages()
    if not avail:
        return preferred_lang or "en"

    if preferred_lang:
        # Exact match or prefix match (e.g. 'en' matches 'en-US')
        for a in avail:
            if a.lower() == preferred_lang.lower() or a.lower().startswith(preferred_lang.lower()):
                return a

    # Default to first available installed language pack
    return avail[0]


def recognize_text(image: Image.Image, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Extracts text and word bounding boxes from an image using Windows OCR.
    """
    if not winocr:
        raise ImportError("winocr is not installed. Install with: pip install winocr")

    attach_desktop()
    set_dpi_awareness()

    actual_lang = _resolve_language(lang)
    result = winocr.recognize_pil_sync(image, lang=actual_lang)
    return result


def find_text(
    query: str,
    image: Optional[Image.Image] = None,
    window: Optional[Union[str, WindowInfo, int]] = None,
    exact: bool = False,
    case_sensitive: bool = False,
    lang: Optional[str] = None,
) -> List[TextMatch]:
    """
    Locates text on the screen or inside a window.
    Returns TextMatch instances with screen-absolute bounding boxes and centers.
    """
    offset_x = 0
    offset_y = 0

    if image is None:
        if window is not None:
            image, win_info = capture_window(window, focus=True)
            offset_x = win_info.left
            offset_y = win_info.top
        else:
            image = capture_screen(all_monitors=True)

    ocr_res = recognize_text(image, lang=lang)
    pattern = query if exact else re.escape(query)
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(f"^{pattern}$" if exact else pattern, flags)

    matches: List[TextMatch] = []

    # First check individual words
    for line in ocr_res.get("lines", []):
        line_text = line.get("text", "")

        # Check line as a whole
        if regex.search(line_text):
            words = line.get("words", [])
            if words:
                min_x = min(w["bounding_rect"]["x"] for w in words)
                min_y = min(w["bounding_rect"]["y"] for w in words)
                max_x = max(w["bounding_rect"]["x"] + w["bounding_rect"]["width"] for w in words)
                max_y = max(w["bounding_rect"]["y"] + w["bounding_rect"]["height"] for w in words)

                rect = (
                    int(min_x + offset_x),
                    int(min_y + offset_y),
                    int(max_x + offset_x),
                    int(max_y + offset_y),
                )
                matches.append(TextMatch(text=line_text, rect=rect))

        # Check individual words
        for w in line.get("words", []):
            w_text = w.get("text", "")
            if regex.search(w_text):
                br = w["bounding_rect"]
                rect = (
                    int(br["x"] + offset_x),
                    int(br["y"] + offset_y),
                    int(br["x"] + br["width"] + offset_x),
                    int(br["y"] + br["height"] + offset_y),
                )
                matches.append(TextMatch(text=w_text, rect=rect))

    return matches


def click_text(
    query: str,
    window: Optional[Union[str, WindowInfo, int]] = None,
    exact: bool = False,
    button: str = "left",
    lang: Optional[str] = None,
) -> Optional[Tuple[int, int]]:
    """
    Finds text on the screen or in a window and clicks its center coordinate.
    Returns the (x, y) coordinates clicked, or None if text was not found.
    """
    matches = find_text(query, window=window, exact=exact, lang=lang)
    if not matches:
        return None

    target = matches[0]
    cx, cy = target.center
    click(cx, cy, button=button)
    return cx, cy
