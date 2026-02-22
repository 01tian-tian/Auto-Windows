"""Keyboard utilities for Windows desktop automation using pyautogui."""

import time
from typing import Optional

import pyautogui
import pyperclip

from Windows.config.timing import TIMING_CONFIG


def type_text(text: str, delay: Optional[float] = None) -> None:
    """
    Type text into the currently focused input field.
    Supports Chinese and other non-ASCII characters via clipboard.

    Args:
        text: The text to type.
        delay: Delay in seconds after typing. If None, uses default from TIMING_CONFIG.

    Note:
        The input field must be focused before calling this function.
        Use click() to focus on the input field first.

    Example:
        >>> type_text("Hello, World!")
        >>> type_text("你好世界")
    """
    if delay is None:
        delay = TIMING_CONFIG.keyboard.default_type_delay

    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(delay)


def hotkey(*keys: str, delay: Optional[float] = None) -> None:
    """
    Execute a keyboard shortcut by pressing multiple keys in sequence.

    Args:
        *keys: The keys to press in sequence. Keys are pressed in order,
               held down together, then released in reverse order.
        delay: Delay in seconds after executing the hotkey. If None, uses default from TIMING_CONFIG.

    Example:
        >>> hotkey('ctrl', 'c')  # Copy
        >>> hotkey('ctrl', 'v')  # Paste
        >>> hotkey('ctrl', 'shift', 's')  # Save As
        >>> hotkey('alt', 'f4')  # Close window
    """
    if delay is None:
        delay = TIMING_CONFIG.keyboard.default_hotkey_delay

    pyautogui.hotkey(*keys)
    time.sleep(delay)


def press(key: str, delay: Optional[float] = None) -> None:
    """
    Press and release a single key.

    Args:
        key: The key to press (e.g., 'enter', 'escape', 'tab', 'space').
        delay: Delay in seconds after pressing. If None, uses default from TIMING_CONFIG.

    Example:
        >>> press('enter')
        >>> press('escape')
        >>> press('tab')
    """
    if delay is None:
        delay = TIMING_CONFIG.keyboard.default_press_delay

    pyautogui.press(key)
    time.sleep(delay)


__all__ = [
    "type_text",
    "hotkey",
    "press",
]
