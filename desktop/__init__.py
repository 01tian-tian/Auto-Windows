"""Desktop automation module for Windows."""

from Windows.desktop.keyboard import (
    hotkey,
    press,
    type_text,
)
from Windows.desktop.mouse import (
    convert_relative_to_absolute,
    double_tap,
    right_click,
    scroll,
    swipe,
    tap,
)
from Windows.desktop.screenshot import (
    Screenshot,
    get_active_window_title,
    get_screenshot,
)

__all__ = [
    "type_text",
    "hotkey",
    "press",
    "tap",
    "right_click",
    "double_tap",
    "swipe",
    "scroll",
    "convert_relative_to_absolute",
    "Screenshot",
    "get_screenshot",
    "get_active_window_title",
]
