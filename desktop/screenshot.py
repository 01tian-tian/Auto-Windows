"""Screenshot utilities for capturing Windows desktop screen."""

import base64
import ctypes
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageGrab


@dataclass
class Screenshot:
    """Represents a captured screenshot."""

    base64_data: str
    width: int
    height: int


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


def get_screenshot() -> Screenshot:
    """
    Capture a screenshot of the Windows desktop.
    Automatically handles DPI scaling.

    Returns:
        Screenshot object containing base64 data and dimensions.
    """
    dpi_scale = get_dpi_scale()

    img = ImageGrab.grab()
    physical_width, physical_height = img.size

    logical_width = int(physical_width / dpi_scale)
    logical_height = int(physical_height / dpi_scale)

    img = img.resize((logical_width, logical_height), Image.Resampling.LANCZOS)

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=logical_width,
        height=logical_height,
    )


def get_active_window_title() -> str:
    """
    Get the title of the currently active window.

    Returns:
        The window title string, or empty string if failed.
    """
    try:
        import win32gui

        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return win32gui.GetWindowText(hwnd)
    except ImportError:
        print("Note: pywin32 not installed. Install: pip install pywin32")
    except Exception as e:
        print(f"Error getting active window title: {e}")

    return ""
