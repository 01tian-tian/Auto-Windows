"""Configuration module for Windows desktop automation."""

from Windows.config.prompts import SYSTEM_PROMPT
from Windows.config.timing import (
    DeviceTimingConfig,
    KeyboardTimingConfig,
    TimingConfig,
    TIMING_CONFIG,
    get_timing_config,
    update_timing_config,
)


def get_system_prompt(lang: str = "cn") -> str:
    """
    Get system prompt by language.

    Args:
        lang: Language code, 'cn' for Chinese, 'en' for English.

    Returns:
        System prompt string.
    """
    return SYSTEM_PROMPT


__all__ = [
    "SYSTEM_PROMPT",
    "get_system_prompt",
    "DeviceTimingConfig",
    "KeyboardTimingConfig",
    "TimingConfig",
    "TIMING_CONFIG",
    "get_timing_config",
    "update_timing_config",
]
