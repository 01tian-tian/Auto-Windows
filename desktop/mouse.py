"""Mouse utilities for Windows desktop operations."""

import ctypes
import time
from typing import Literal

import pyautogui

from Windows.config.timing import TIMING_CONFIG


def get_dpi_scale() -> float:
    """
    Get the Windows DPI scale factor.

    Returns:
        DPI scale factor (e.g., 1.25 for 125% scaling, 1.5 for 150%).
    """
    try:
        user32 = ctypes.windll.user32
        hdc = user32.GetDC(0)
        LOGPIXELSX = 88
        scale = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX) / 96.0
        user32.ReleaseDC(0, hdc)
        return scale
    except Exception:
        return 1.0


def _scale_coordinates(x: int, y: int) -> tuple[int, int]:
    """
    Scale logical coordinates to physical coordinates based on DPI.

    Args:
        x: Logical x coordinate.
        y: Logical y coordinate.

    Returns:
        Tuple of (physical_x, physical_y) coordinates.
    """
    dpi_scale = get_dpi_scale()
    physical_x = int(x * dpi_scale)
    physical_y = int(y * dpi_scale)
    return (physical_x, physical_y)


def tap(x: int, y: int, delay: float | None = None) -> None:
    """
    Perform a left mouse click at the specified coordinates.

    Args:
        x: The x coordinate in logical pixels (accounts for DPI scaling).
        y: The y coordinate in logical pixels (accounts for DPI scaling).
        delay: Optional delay in seconds after the click. Defaults to TIMING_CONFIG.device.default_tap_delay.
    """
    phys_x, phys_y = _scale_coordinates(x, y)
    pyautogui.click(phys_x, phys_y)
    time.sleep(delay if delay is not None else TIMING_CONFIG.device.default_tap_delay)


def right_click(x: int, y: int, delay: float | None = None) -> None:
    """
    Perform a right mouse click at the specified coordinates.

    Args:
        x: The x coordinate in logical pixels (accounts for DPI scaling).
        y: The y coordinate in logical pixels (accounts for DPI scaling).
        delay: Optional delay in seconds after the click. Defaults to TIMING_CONFIG.device.default_tap_delay.
    """
    phys_x, phys_y = _scale_coordinates(x, y)
    pyautogui.rightClick(phys_x, phys_y)
    time.sleep(delay if delay is not None else TIMING_CONFIG.device.default_tap_delay)


def double_tap(x: int, y: int, delay: float | None = None) -> None:
    """
    Perform a double left mouse click at the specified coordinates.

    Args:
        x: The x coordinate in logical pixels (accounts for DPI scaling).
        y: The y coordinate in logical pixels (accounts for DPI scaling).
        delay: Optional delay in seconds after the double click. Defaults to TIMING_CONFIG.device.default_double_tap_delay.
    """
    phys_x, phys_y = _scale_coordinates(x, y)
    pyautogui.doubleClick(phys_x, phys_y)
    time.sleep(delay if delay is not None else TIMING_CONFIG.device.default_double_tap_delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: float | None = None,
    delay: float | None = None,
) -> None:
    """
    Perform a mouse drag from start coordinates to end coordinates.

    Args:
        start_x: The starting x coordinate in logical pixels.
        start_y: The starting y coordinate in logical pixels.
        end_x: The ending x coordinate in logical pixels.
        end_y: The ending y coordinate in logical pixels.
        duration_ms: Optional duration of the drag in milliseconds. Defaults to 300ms.
        delay: Optional delay in seconds after the swipe. Defaults to TIMING_CONFIG.device.default_swipe_delay.
    """
    phys_start_x, phys_start_y = _scale_coordinates(start_x, start_y)
    phys_end_x, phys_end_y = _scale_coordinates(end_x, end_y)

    duration = (duration_ms if duration_ms is not None else 300) / 1000.0
    pyautogui.moveTo(phys_start_x, phys_start_y)
    pyautogui.drag(phys_end_x - phys_start_x, phys_end_y - phys_start_y, duration=duration)
    time.sleep(delay if delay is not None else TIMING_CONFIG.device.default_swipe_delay)


def scroll(
    direction: Literal["up", "down"],
    amount: int = 10,
    delay: float | None = None,
) -> None:
    """
    Perform a mouse scroll in the specified direction.

    Args:
        direction: The scroll direction, either "up" or "down".
        amount: The number of scroll clicks. Defaults to 10 for larger scroll distance.
        delay: Optional delay in seconds after the scroll. Defaults to TIMING_CONFIG.device.default_scroll_delay.
    """
    scroll_amount = amount if direction == "up" else -amount
    pyautogui.scroll(scroll_amount)
    time.sleep(delay if delay is not None else TIMING_CONFIG.device.default_scroll_delay)


def convert_relative_to_absolute(
    element: list[int] | list[float],
    screen_width: int,
    screen_height: int,
) -> tuple[int, int]:
    """
    Convert relative coordinates to absolute logical pixel coordinates.
    Automatically detects coordinate range:
    - If values are <= 1, treats as 0-1 range (percentage)
    - If values are <= 999, treats as 0-999 range
    - Otherwise treats as absolute pixels

    Args:
        element: A list containing [x, y] relative coordinates.
        screen_width: The screen width in logical pixels.
        screen_height: The screen height in logical pixels.

    Returns:
        A tuple of (x, y) absolute logical pixel coordinates.

    Example:
        >>> convert_relative_to_absolute([500, 500], 1920, 1080)
        (960, 540)
        >>> convert_relative_to_absolute([0.5, 0.5], 1920, 1080)
        (960, 540)
    """
    rel_x, rel_y = element

    if rel_x <= 1.0 and rel_y <= 1.0:
        abs_x = int(rel_x * screen_width)
        abs_y = int(rel_y * screen_height)
    elif rel_x <= 999 and rel_y <= 999:
        abs_x = int(rel_x * screen_width / 1000)
        abs_y = int(rel_y * screen_height / 1000)
    else:
        abs_x = int(rel_x)
        abs_y = int(rel_y)

    return (abs_x, abs_y)


__all__ = [
    "tap",
    "right_click",
    "double_tap",
    "swipe",
    "scroll",
    "convert_relative_to_absolute",
    "get_dpi_scale",
]
