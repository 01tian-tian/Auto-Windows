"""Action handler for processing AI model outputs on Windows desktop."""

import ast
import re
import time
from dataclasses import dataclass
from typing import Any, Callable

from Windows.config.timing import TIMING_CONFIG
from Windows.desktop import (
    convert_relative_to_absolute,
    double_tap,
    hotkey,
    press,
    right_click,
    scroll,
    swipe,
    tap,
    type_text,
)


@dataclass
class ActionResult:
    """Result of an action execution."""

    success: bool
    should_finish: bool
    message: str | None = None
    requires_confirmation: bool = False


class ActionHandler:
    """
    Handles execution of actions from AI model output on Windows desktop.

    Args:
        confirmation_callback: Optional callback for sensitive action confirmation.
            Should return True to proceed, False to cancel.
        takeover_callback: Optional callback for takeover requests (login, captcha).
    """

    def __init__(
        self,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.takeover_callback = takeover_callback or self._default_takeover

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        """
        Execute an action from the AI model.

        Args:
            action: The action dictionary from the model.
            screen_width: Current screen width in pixels.
            screen_height: Current screen height in pixels.

        Returns:
            ActionResult indicating success and whether to finish.
        """
        action_type = action.get("_metadata")

        if action_type == "finish":
            return ActionResult(
                success=True, should_finish=True, message=action.get("message")
            )

        if action_type != "do":
            return ActionResult(
                success=False,
                should_finish=True,
                message=f"Unknown action type: {action_type}",
            )

        action_name = action.get("action")
        handler_method = self._get_handler(action_name)

        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action: {action_name}",
            )

        try:
            return handler_method(action, screen_width, screen_height)
        except Exception as e:
            return ActionResult(
                success=False, should_finish=False, message=f"Action failed: {e}"
            )

    def _get_handler(self, action_name: str) -> Callable | None:
        """Get the handler method for an action."""
        handlers = {
            "Tap": self._handle_tap,
            "RightClick": self._handle_right_click,
            "DoubleTap": self._handle_double_tap,
            "Type": self._handle_type,
            "Hotkey": self._handle_hotkey,
            "Swipe": self._handle_swipe,
            "Scroll": self._handle_scroll,
            "Wait": self._handle_wait,
            "Take_over": self._handle_takeover,
            "Launch": self._handle_launch,
        }
        return handlers.get(action_name)

    def _handle_launch(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle launch action - not supported, return error."""
        return ActionResult(
            success=False,
            should_finish=False,
            message="Launch命令不支持。请使用Hotkey(win)打开开始菜单，然后搜索应用；或使用Hotkey(win+d)显示桌面后双击图标。",
        )

    def _convert_relative_to_absolute(
        self, element: list[int], screen_width: int, screen_height: int
    ) -> tuple[int, int]:
        """Convert relative coordinates (0-999) to absolute pixels."""
        return convert_relative_to_absolute(element, screen_width, screen_height)

    def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle tap action (left click)."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)

        if "message" in action:
            if not self.confirmation_callback(action["message"]):
                return ActionResult(
                    success=False,
                    should_finish=True,
                    message="User cancelled sensitive operation",
                )

        tap(x, y)
        time.sleep(TIMING_CONFIG.device.default_tap_delay)
        return ActionResult(True, False)

    def _handle_right_click(
        self, action: dict, width: int, height: int
    ) -> ActionResult:
        """Handle right click action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        right_click(x, y)
        time.sleep(TIMING_CONFIG.device.default_tap_delay)
        return ActionResult(True, False)

    def _handle_double_tap(
        self, action: dict, width: int, height: int
    ) -> ActionResult:
        """Handle double tap action (double click)."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        double_tap(x, y)
        time.sleep(TIMING_CONFIG.device.default_double_tap_delay)
        return ActionResult(True, False)

    def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle text input action."""
        text = action.get("text", "")
        type_text(text)
        time.sleep(TIMING_CONFIG.keyboard.default_type_delay)
        return ActionResult(True, False)

    def _handle_hotkey(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle hotkey action."""
        keys = action.get("keys", "")
        if not keys:
            return ActionResult(False, False, "No keys specified")

        hotkey(keys)
        time.sleep(TIMING_CONFIG.keyboard.default_hotkey_delay)
        return ActionResult(True, False)

    def _handle_swipe(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle swipe action (drag)."""
        start = action.get("start")
        end = action.get("end")

        if not start or not end:
            return ActionResult(False, False, "Missing swipe coordinates")

        start_x, start_y = self._convert_relative_to_absolute(start, width, height)
        end_x, end_y = self._convert_relative_to_absolute(end, width, height)

        swipe(start_x, start_y, end_x, end_y)
        time.sleep(TIMING_CONFIG.device.default_swipe_delay)
        return ActionResult(True, False)

    def _handle_scroll(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle scroll action."""
        direction = action.get("direction", "down")
        amount = action.get("amount", 3)

        try:
            amount = int(amount)
        except (ValueError, TypeError):
            amount = 3

        scroll(direction, amount)
        time.sleep(TIMING_CONFIG.device.default_scroll_delay)
        return ActionResult(True, False)

    def _handle_wait(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle wait action."""
        duration_str = action.get("duration", "1 seconds")
        try:
            duration = float(duration_str.replace("seconds", "").strip())
        except ValueError:
            duration = 1.0

        time.sleep(duration)
        return ActionResult(True, False)

    def _handle_takeover(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle takeover request (login, captcha, etc.)."""
        message = action.get("message", "User intervention required")
        self.takeover_callback(message)
        return ActionResult(True, False)

    @staticmethod
    def _default_confirmation(message: str) -> bool:
        """Default confirmation callback using console input."""
        response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
        return response.upper() == "Y"

    @staticmethod
    def _default_takeover(message: str) -> None:
        """Default takeover callback using console input."""
        input(f"{message}\nPress Enter after completing manual operation...")


def parse_action(response: str) -> dict[str, Any]:
    """
    Parse action from model response.

    Args:
        response: Raw response string from the model.

    Returns:
        Parsed action dictionary with optional 'thinking' field.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    try:
        response = response.strip()

        thinking = None
        thinking_match = re.search(r'思考:\s*(.+?)(?=动作:|$)', response, re.DOTALL)
        if thinking_match:
            thinking = thinking_match.group(1).strip()

        action_match = re.search(r'动作:\s*(.+?)$', response, re.DOTALL)
        if action_match:
            response = action_match.group(1).strip()

        response = re.sub(r'</answer>\s*$', '', response)
        response = re.sub(r'</think_tag>\s*$', '', response)

        if response.startswith("do"):
            try:
                response = response.replace("\n", "\\n")
                response = response.replace("\r", "\\r")
                response = response.replace("\t", "\\t")

                if not response.endswith(")"):
                    match = re.search(r'do\([^)]+\)', response)
                    if match:
                        response = match.group(0)

                tree = ast.parse(response, mode="eval")
                if not isinstance(tree.body, ast.Call):
                    raise ValueError("Expected a function call")

                call = tree.body
                action = {"_metadata": "do"}
                for keyword in call.keywords:
                    key = keyword.arg
                    value = ast.literal_eval(keyword.value)
                    action[key] = value

                if thinking:
                    action["thinking"] = thinking
                return action
            except (SyntaxError, ValueError) as e:
                raise ValueError(f"Failed to parse do() action: {e}")

        elif response.startswith("finish"):
            match = re.search(r'finish\(message="([^"]*)"\)', response)
            if match:
                message = match.group(1)
            else:
                message = response.replace("finish(message=", "")
                if message.startswith('"') and message.endswith('"'):
                    message = message[1:-1]
            action = {
                "_metadata": "finish",
                "message": message,
            }
            if thinking:
                action["thinking"] = thinking
        else:
            raise ValueError(f"Failed to parse action: {response}")
        return action
    except Exception as e:
        raise ValueError(f"Failed to parse action: {e}")


def do(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'do' actions."""
    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'finish' actions."""
    kwargs["_metadata"] = "finish"
    return kwargs
