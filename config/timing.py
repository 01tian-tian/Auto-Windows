"""Timing configuration for Windows desktop automation.

This module defines all configurable waiting times used throughout the application.
Users can customize these values by modifying this file or by setting environment variables.
"""

import os
from dataclasses import dataclass


@dataclass
class KeyboardTimingConfig:
    """Configuration for keyboard operation timing delays."""

    default_type_delay: float = 0.1
    default_hotkey_delay: float = 0.1
    default_press_delay: float = 0.1

    def __post_init__(self):
        """Load values from environment variables if present."""
        self.default_type_delay = float(
            os.getenv("WINDOWS_TYPE_DELAY", self.default_type_delay)
        )
        self.default_hotkey_delay = float(
            os.getenv("WINDOWS_HOTKEY_DELAY", self.default_hotkey_delay)
        )
        self.default_press_delay = float(
            os.getenv("WINDOWS_PRESS_DELAY", self.default_press_delay)
        )


@dataclass
class DeviceTimingConfig:
    """Configuration for device operation timing delays."""

    default_tap_delay: float = 1.0
    default_double_tap_delay: float = 1.0
    default_swipe_delay: float = 1.0
    default_scroll_delay: float = 1.0

    def __post_init__(self):
        """Load values from environment variables if present."""
        self.default_tap_delay = float(
            os.getenv("WINDOWS_TAP_DELAY", self.default_tap_delay)
        )
        self.default_double_tap_delay = float(
            os.getenv("WINDOWS_DOUBLE_TAP_DELAY", self.default_double_tap_delay)
        )
        self.default_swipe_delay = float(
            os.getenv("WINDOWS_SWIPE_DELAY", self.default_swipe_delay)
        )
        self.default_scroll_delay = float(
            os.getenv("WINDOWS_SCROLL_DELAY", self.default_scroll_delay)
        )


@dataclass
class TimingConfig:
    """Master timing configuration combining all timing settings."""

    keyboard: KeyboardTimingConfig
    device: DeviceTimingConfig

    def __init__(self):
        """Initialize all timing configurations."""
        self.keyboard = KeyboardTimingConfig()
        self.device = DeviceTimingConfig()


TIMING_CONFIG = TimingConfig()


def get_timing_config() -> TimingConfig:
    """
    Get the global timing configuration.

    Returns:
        The global TimingConfig instance.
    """
    return TIMING_CONFIG


def update_timing_config(
    keyboard: KeyboardTimingConfig | None = None,
    device: DeviceTimingConfig | None = None,
) -> None:
    """
    Update the global timing configuration.

    Args:
        keyboard: New keyboard timing configuration.
        device: New device timing configuration.

    Example:
        >>> from Windows.config.timing import update_timing_config, KeyboardTimingConfig
        >>> custom_keyboard = KeyboardTimingConfig(
        ...     default_type_delay=0.05,
        ...     default_press_delay=0.05
        ... )
        >>> update_timing_config(keyboard=custom_keyboard)
    """
    global TIMING_CONFIG
    if keyboard is not None:
        TIMING_CONFIG.keyboard = keyboard
    if device is not None:
        TIMING_CONFIG.device = device


__all__ = [
    "KeyboardTimingConfig",
    "DeviceTimingConfig",
    "TimingConfig",
    "TIMING_CONFIG",
    "get_timing_config",
    "update_timing_config",
]
